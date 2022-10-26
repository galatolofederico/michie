import dataclasses
from tqdm import trange
import multiprocessing
import time
import orjson
import os
from lru import LRU

from michie.object import Object
from michie.worker import Worker, Works
from michie.transitions import Transition
from michie.mappers import StateMapper
from michie.serialize import serialize, deserialize

FORCE_SYNC = bool(os.environ.get("MICHIE_FORCE_SYNC", False))
DISABLE_CACHE = bool(os.environ.get("MICHIE_DISABLE_CACHE", False))

class World:
    def __init__(self, *, global_mappers=[], tick_hooks=[], lru_cache_size=10_000):
        self.global_mappers = global_mappers
        self.tick_hooks = tick_hooks
        self.cache = LRU(lru_cache_size)
        self.global_state = dict(
            tick=0,
            michie=dict(stats=dict())
        )
        self.objects = []
        self.dict_states = []
        self.state_mappers = dict()
        self.state_mappers_ids = []
        self.transitions = dict()
        self.transitions_ids = []
        self.window = None
        self.render_surface = None
    
    def add_object(self, object):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        object.init["type"] = object.name
        object.init["id"] = len(self.objects)

        transitions_ids = []
        for transition in object.transitions:
            if not transition.__name__ in self.transitions:
                self.transitions[transition.__name__] = transition
            transitions_ids.append(transition.__name__)
        self.transitions_ids.append(transitions_ids)

        state_mappers_ids = []
        for state_mapper in object.state_mappers:
            if not state_mapper.__name__ in self.state_mappers:
                self.state_mappers[state_mapper.__name__] = state_mapper
            state_mappers_ids.append(state_mapper.__name__)
        self.state_mappers_ids.append(state_mappers_ids)

        self.objects.append(object)
        self.dict_states.append(object.init)

    def make_async_work(self, *, work_id, id, operation, operation_id, state):
        work = None
        if issubclass(operation, Transition):
            work = dict(
                type = Works.STATE_TRANSITION.value,
                work_id = work_id,
                args = dict(
                    id = id,
                    state = operation.state_map(state),
                    transition_id = operation_id,
                ),
            )
        elif issubclass(operation, StateMapper):
            work = dict(
                type = Works.STATE_MAP.value,
                work_id = work_id,
                args = dict(
                    id = id,
                    state = operation.state_map(state),
                    global_state = operation.global_state_map(self.global_state),
                    state_mapper_id = operation_id
                )
            )
        else:
            raise Exception(f"Unknown operation {operation}")
        
        try:
            return serialize(work)
        except Exception as e:
            print("Serialization error for work")
            print(work)
            raise e
    
    def run_sync_work(self, *, operation, id, state):
        if issubclass(operation, Transition):
            return operation.transition(
                operation.state_map(state)
            )
        elif issubclass(operation, StateMapper):
            return operation.map(
                id,
                operation.state_map(state),
                operation.global_state_map(self.global_state)
            )
    
    def run_works(self, *, operation, submit_queue, results_queue):
        start_operation_time = time.time()
        assert operation == "transitions" or operation == "state_mappers"
        assert submit_queue.empty() and results_queue.empty()

        operations = self.transitions if operation == "transitions" else self.state_mappers
        operations_ids = self.transitions_ids if operation == "transitions" else self.state_mappers_ids
        operation_name = operation

        async_works = 0
        sync_works = 0
        cached_works = 0
        
        results = []
        async_cache_keys = dict()
        start_work_build_time = time.time()
        for id, (state, operation_ids) in enumerate(zip(self.dict_states, operations_ids)):
            for operation_id in operation_ids:
                operation = operations[operation_id]
                requirements = operation.requirements(state)
                cache_key = ""
                if not DISABLE_CACHE and hasattr(operation, "cache_key") and requirements:
                    if issubclass(operation, Transition):
                        cache_key = ("transition", operation.__name__, operation.cache_key(state))
                    elif issubclass(operation, StateMapper):
                        cache_key = ("state-mapper", operation.__name__, operation.cache_key(state, self.global_state))

                    if cache_key in self.cache:
                        cached_works += 1
                        results.append(dict(
                            id=id,
                            cache_key=cache_key,
                            cache_hit=1,
                            result=self.cache[cache_key]
                        ))
                        continue

                if (not FORCE_SYNC and not operation.sync()) and requirements:
                    async_works += 1
                    async_cache_keys[async_works] = cache_key
                    submit_queue.put(
                        self.make_async_work(
                            work_id=async_works,
                            id=id,
                            operation=operation,
                            operation_id=operation_id,
                            state=state,
                        )
                    )
                if (FORCE_SYNC or operation.sync()) and requirements:
                    sync_works += 1
                    results.append(dict(
                        id=id,
                        cache_key=cache_key,
                        cache_hit=0,
                        result=self.run_sync_work(
                            id=id,
                            operation=operation,
                            state=state,
                        )
                    ))
        end_work_build_time = time.time()

        start_sync_and_cache_join_results = time.time()
        for result in results:
            self.dict_states[result["id"]].update(result["result"])  
            if result["cache_key"] != "" and not result["cache_hit"]:
                self.cache[cache_key] = result["result"]
        end_sync_and_cache_join_results = time.time()

        start_async_join_results = time.time()
        for _ in range(0, async_works):
            result = results_queue.get()
            result = deserialize(result)
            self.dict_states[result["id"]].update(result["result"])
            cache_key = async_cache_keys[result["work_id"]]
            if cache_key != "":
                self.cache[cache_key] = result["result"]
        end_async_join_results = time.time()
        
        end_operation_time = time.time()
        self.global_state["michie"]["stats"][f"{operation_name}/work_build_time"] = end_work_build_time - start_work_build_time
        self.global_state["michie"]["stats"][f"{operation_name}/sync_and_cache_join_results"] = end_sync_and_cache_join_results - start_sync_and_cache_join_results
        self.global_state["michie"]["stats"][f"{operation_name}/async_join_results"] = end_async_join_results - start_async_join_results
        self.global_state["michie"]["stats"][f"{operation_name}/async_works"] = async_works
        self.global_state["michie"]["stats"][f"{operation_name}/sync_works"] = sync_works
        self.global_state["michie"]["stats"][f"{operation_name}/cached_works"] = cached_works
        self.global_state["michie"]["stats"][f"{operation_name}_execution_time"] = end_operation_time - start_operation_time
        
        assert submit_queue.empty() and results_queue.empty()
    
    def run_global_mappers(self):
        start_time = time.time()
        for global_mapper in self.global_mappers:
            self.dict_states = global_mapper.map(self.dict_states, self.global_state) 
        end_time = time.time()
        self.global_state["michie"]["stats"]["global_mappers_execution_time"] = end_time - start_time

    def render(self, *, window, clock, fps=30, background="black"):
        start_time = time.time()
        import pygame
        window.fill(background)
        sprites = [object.sprites for object in self.objects]
        for state, object_sprites in zip(self.dict_states, sprites):
            for object_sprite in object_sprites: object_sprite.draw(window=window, state=state)
        pygame.display.flip()
        if clock is not None: clock.tick(fps)
        end_time = time.time()
        self.global_state["michie"]["stats"]["render_time"] = end_time - start_time

    def run(
            self,
            *,
            workers,
            max_ticks=100,
            render=False,
            render_surface=(800, 600),
            render_fps=None,
            render_background="black"
        ):
        if FORCE_SYNC: print("Warning: michie parallelism is disabled by MICHIE_FORCE_SYNC")
        if DISABLE_CACHE: print("Warning: michie cache is disabled by MICHIE_DISABLE_CACHE")
        
        if render:
            import pygame
            pygame.init()
            window = pygame.display.set_mode(render_surface, pygame.HWSURFACE | pygame.DOUBLEBUF)
            clock = None
            if render_fps is not None:
                clock = pygame.time.Clock()

        submit_queue = multiprocessing.Queue()
        results_queue = multiprocessing.Queue()
        
        workers = [
            Worker(
                id=id,
                submit_queue=submit_queue,
                results_queue=results_queue,
                state_mappers=self.state_mappers,
                transitions=self.transitions
            ) for id in range(0, workers)
        ]
        [worker.start() for worker in workers]
        for hook in self.tick_hooks: hook.start(self.dict_states, self.global_state, window)
        
        for i in trange(0, max_ticks):
            start_tick_time = time.time()
            self.run_global_mappers()
            self.run_works(operation="state_mappers", submit_queue=submit_queue, results_queue=results_queue)
            self.run_works(operation="transitions", submit_queue=submit_queue, results_queue=results_queue)
            self.global_state["tick"] += 1

            if render: self.render(
                window=window,
                clock=clock,
                fps=render_fps,
                background=render_background
            )
            end_tick_time = time.time()
            self.global_state["michie"]["stats"]["tick_time"] = end_tick_time - start_tick_time
            for hook in self.tick_hooks: hook.tick(self.dict_states, self.global_state, window)
        
        for hook in self.tick_hooks: hook.end(self.dict_states, self.global_state, window)

        for i in range(0, len(workers)):
            submit_queue.put(serialize(dict(
                type=Works.EXIT.value
            )))