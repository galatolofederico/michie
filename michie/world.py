import dataclasses
from tqdm import trange
import multiprocessing
import time
import orjson

from michie.object import Object
from michie.worker import Worker, Works
from michie.serialize import serialize, deserialize

class World:
    def __init__(self, *, global_mappers=[], tick_hooks=[], config=None):
        self.config = config
        self.global_mappers = global_mappers
        self.tick_hooks = tick_hooks
        self.global_state = dict(
            tick=0,
            michie=dict(stats=self.init_stats())
        )
        self.objects = []
        self.dict_states = []
        self.state_mappers = dict()
        self.state_mappers_ids = []
        self.transitions = dict()
        self.transitions_ids = []
        self.window = None
        self.render_surface = None
    
    def init_stats(self):
        return dict(
            global_mappers_execution_time=0,
            transitions_submission_time=0,
            transitions_retrieval_time=0,
            transitions_works=0,
            state_mappers_submission_time=0,
            state_mappers_retrieval_time=0,
            state_mappers_works=0,
            render_time=0
        )

    def add_object(self, object):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        object.init["type"] = object.name

        transitions_ids = []
        for transition in object.transitions:
            if not transition.__name__ in self.transitions:
                self.transitions[transition.__name__] = transition
            transitions_ids.append(transition.__name__)
        self.transitions_ids.append(transitions_ids)

        state_mappers_ids = []
        for transition in object.state_mappers:
            if not transition.__name__ in self.state_mappers:
                self.state_mappers[transition.__name__] = transition
            state_mappers_ids.append(transition.__name__)
        self.state_mappers_ids.append(state_mappers_ids)

        self.objects.append(object)
        self.dict_states.append(object.init)

    def transitions_tick(self, *, submit_queue, results_queue):
        assert submit_queue.empty() and results_queue.empty()

        start_submission_time = time.time()
        works = 0
        for id, (state, transitions_ids) in enumerate(zip(self.dict_states, self.transitions_ids)):
            for transition_id in transitions_ids:
                transition = self.transitions[transition_id]
                if transition.requirements(state):
                    work = dict(
                        type = Works.STATE_TRANSITION.value,
                        args = dict(
                            id = id,
                            state = transition.state_map(state),
                            transition_id = transition_id
                        )
                    )
                    try:
                        submit_queue.put(serialize(work))
                    except Exception as e:
                        print("Serialization error for work")
                        print(work)
                        raise e
                    
                    works += 1
        
        end_submission_time = time.time()
        for _ in range(0, works):
            result = results_queue.get()
            result = deserialize(result)
            self.dict_states[result["id"]].update(result["result"])  
        end_retrieve_time = time.time()

        self.global_state["michie"]["stats"]["transitions_submission_time"] = end_submission_time - start_submission_time
        self.global_state["michie"]["stats"]["transitions_retrieval_time"] = end_retrieve_time - end_submission_time
        self.global_state["michie"]["stats"]["transitions_works"] = works

        assert submit_queue.empty() and results_queue.empty()
    
    def map_states(self, *, submit_queue, results_queue):
        assert submit_queue.empty() and results_queue.empty()

        start_submission_time = time.time()
        works = 0
        for id, (state, state_mappers_ids) in enumerate(zip(self.dict_states, self.state_mappers_ids)):
            for state_mapper_id in state_mappers_ids:
                mapper = self.state_mappers[state_mapper_id]
                if mapper.requirements(state):
                    work = dict(
                        type = Works.STATE_MAP.value,
                        args = dict(
                            id = id,
                            state = mapper.state_map(state),
                            global_state = mapper.global_state_map(self.global_state),
                            state_mapper_id = state_mapper_id
                        )
                    )
                    try:
                        submit_queue.put(serialize(work))
                    except Exception as e:
                        print("Serialization error for work")
                        print(work)
                        raise e

                    works += 1
        
        end_submission_time = time.time()
        for _ in range(0, works):
            result = results_queue.get()
            result = deserialize(result)
            self.dict_states[result["id"]].update(result["result"])  
        end_retrieve_time = time.time()

        self.global_state["michie"]["stats"]["state_mappers_submission_time"] = end_submission_time - start_submission_time
        self.global_state["michie"]["stats"]["state_mappers_retrieval_time"] = end_retrieve_time - end_submission_time
        self.global_state["michie"]["stats"]["state_mappers_works"] = works

        assert submit_queue.empty() and results_queue.empty()

    def global_map_states(self):
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
            self.global_map_states()
            self.map_states(submit_queue=submit_queue, results_queue=results_queue)
            self.transitions_tick(submit_queue=submit_queue, results_queue=results_queue)
            self.global_state["tick"] += 1

            if render: self.render(
                window=window,
                clock=clock,
                fps=render_fps,
                background=render_background
            )
            for hook in self.tick_hooks: hook.tick(self.dict_states, self.global_state, window)
        
        for hook in self.tick_hooks: hook.end(self.dict_states, self.global_state, window)

        for i in range(0, len(workers)):
            submit_queue.put(serialize(dict(
                type=Works.EXIT.value
            )))