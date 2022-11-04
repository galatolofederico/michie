import dataclasses
from tqdm import trange
import multiprocessing
import time
import orjson
import os
from lru import LRU
import flatdict
import copy

from michie.object import Object
from michie.worker import Worker
from michie.transitions import Transition
from michie.mappers import StateMapper
from michie.messages import Commands, send_msg, recv_msg


class World:
    def __init__(
            self,
            *,
            workers=-1,
            global_mappers=[],
            retrieve_map_state=None,
            submit_map_global_state=None,
            tick_hooks=[],
            strict_update=False,
            lru_cache_size=10_000
        ):
        self.num_workers = workers if workers > 0 else os.cpu_count()
        self.global_mappers = global_mappers
        self.retrieve_map_state = retrieve_map_state if retrieve_map_state is not None else lambda g: g
        self.submit_map_global_state = submit_map_global_state if submit_map_global_state is not None else lambda g: g
        self.tick_hooks = tick_hooks
        
        self.global_state = dict(tick=0)
        self.window = None
        self.render_surface = None
        self.objects = []

        self.init_workers()

    def init_workers(self):
        self.current_submit_worker = 0
        self.workers = []
        for id in range(0, self.num_workers):
            submit_queue=multiprocessing.Queue()
            results_queue=multiprocessing.Queue()
            worker = Worker(
                id=id,
                submit_queue=submit_queue,
                results_queue=results_queue,
                retrieve_map_state=self.retrieve_map_state
            )

            self.workers.append(dict(
                submit_queue=submit_queue,
                results_queue=results_queue,
                worker=worker
            ))
    
    def add_object(self, object):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        object.init["type"] = object.name
        object.id = len(self.objects)
        object.init["id"] = object.id

        self.workers[self.current_submit_worker]["worker"].add_object(object)
        self.objects.append(object)

        self.current_submit_worker = (self.current_submit_worker + 1) % len(self.workers)
    
    def run_global_mappers(self, states):
        current_states = [s["state"] for s in states]
        workers_ids = [s["worker_id"] for s in states]
        objects_ids = [s["object_id"] for s in states]
        
        for global_mapper in self.global_mappers:
            current_states = global_mapper.map(current_states, self.global_state) 
        
        workers_states = dict()
        for worker_id, object_id, state in zip(workers_ids, objects_ids, current_states):
            if not worker_id in workers_states: workers_states[worker_id] = []
            workers_states[worker_id].append(dict(
                object_id=object_id,
                state=state
            ))
 
        for worker_id, states in workers_states.items():
            send_msg(
                to=self.workers[worker_id],
                serialize=True,
                msg=dict(
                    cmd=Commands.SET_STATE.value,
                    args=dict(
                        states=states
                    )
                )
            )
        
        for worker in self.workers:
            reply = recv_msg(worker)
            assert reply["cmd"] == Commands.STATE_SET.value


    def workers_tick(self):
        for worker in self.workers:
            send_msg(
                to=worker,
                serialize=True,
                msg=dict(
                    cmd=Commands.DO_TICK.value,
                    args=dict(
                        global_state=self.submit_map_global_state(self.global_state)
                    )
                )
            )
        
        for worker in self.workers:
            reply = recv_msg(worker)
            assert reply["cmd"] == Commands.TICK_DONE.value

    def retrieve_states(self):
        states = []
        for worker in self.workers:
            send_msg(
                to=worker,
                serialize=False,
                msg=dict(
                    cmd=Commands.RETRIEVE_STATE.value,
                    args=dict()
                )
            )
        
        for worker in self.workers:
            worker_states = recv_msg(worker)
            assert worker_states["cmd"] == Commands.STATE.value
            for worker_state in worker_states["args"]["states"]:
                states.append(worker_state)
        
        states = sorted(states, key=lambda s: s["object_id"])
        return states


    def render(self, *, states, window, clock, fps=30, background="black"):
        import pygame
        window.fill(background)
        sprites = [object.sprites for object in self.objects]
        states = [s["state"] for s in states]
        for state, object_sprites in zip(states, sprites):
            for object_sprite in object_sprites: object_sprite.draw(window=window, state=state)
        pygame.display.flip()
        if clock is not None: clock.tick(fps)


    def run(
            self,
            *,
            max_ticks=100,
            render=False,
            render_surface=(800, 600),
            render_fps=None,
            render_background="black"
        ):
        
        for worker in self.workers: worker["worker"].start()

        if render:
            import pygame
            pygame.init()
            window = pygame.display.set_mode(render_surface, pygame.HWSURFACE | pygame.DOUBLEBUF)
            clock = None
            if render_fps is not None:
                clock = pygame.time.Clock()

        for hook in self.tick_hooks: hook.start(self.dict_states, self.global_state, window)
        
        for i in trange(0, max_ticks):
            self.global_state["tick"] += 1

            states = self.retrieve_states()
            self.run_global_mappers(states)
            self.workers_tick()
            
            if render: self.render(
                states=states,
                window=window,
                clock=clock,
                fps=render_fps,
                background=render_background
            )

            for hook in self.tick_hooks: hook.tick(self.dict_states, self.global_state, window)
            
        
        for hook in self.tick_hooks: hook.end(self.dict_states, self.global_state, window)
        
        for worker in self.workers:
            send_msg(
                to=worker,
                serialize=False,
                msg=dict(
                    cmd=Commands.EXIT.value,
                    args=dict()
                )
            )
        