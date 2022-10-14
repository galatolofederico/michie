import dataclasses
from tqdm import trange
import multiprocessing

from michie.object import Object
from michie.worker import Worker, Works

class World:
    def __init__(self, *, global_mappers=[], config=None):
        self.config = config
        self.global_mappers = global_mappers
        self.global_state = dict()
        self.objects = []
        self.dict_states = []
        self.transitions = dict()
        self.transitions_ids = []
        self.window = None
        self.render_surface = None
    
    def add_object(self, *, object, init):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        schema = object.state.validate(init)

        transitions_ids = []
        for transition in object.transitions:
            if not transition.__name__ in self.transitions:
                self.transitions[transition.__name__] = transition
            transitions_ids.append(transition.__name__)
        self.transitions_ids.append(transitions_ids)

        self.objects.append(object)
        self.dict_states.append(init)
    
    def run_works(self, *, works, submit_queue, results_queue):
        assert submit_queue.empty() and results_queue.empty()
        
        [submit_queue.put(work) for work in works]
        
        results = [results_queue.get() for i in range(0, len(works))]
        results = sorted(results, key=lambda e: e["id"])
        results = tuple(map(lambda e: e["result"], results))
        
        assert submit_queue.empty() and results_queue.empty()
        return results

    def transitions_tick(self, *, submit_queue, results_queue):
        works = []        
        for id, (state, transitions_ids) in enumerate(zip(self.dict_states, self.transitions_ids)):
            works.append(dict(
                type = Works.STATE_TRANSITION,
                args = dict(
                    id = id,
                    state = state,
                    transitions_ids = transitions_ids
                )
            ))
        
        self.dict_states = self.run_works(
            works=works,
            submit_queue=submit_queue,
            results_queue=results_queue
        )
        
    def render(self, *, window, clock, fps=30, background="black"):
        import pygame
        window.fill(background)
        sprites = [object.sprites for object in self.objects]
        for state, object_sprites in zip(self.dict_states, sprites):
            for object_sprite in object_sprites: object_sprite.draw(window=window, state=state)
        pygame.display.flip()
        if clock is not None: clock.tick(fps)

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
                submit_queue=submit_queue,
                results_queue=results_queue,
                transitions=self.transitions
            ) for _ in range(0, workers)
        ]
        [worker.start() for worker in workers]

        for i in trange(0, max_ticks):
            for global_mapper in self.global_mappers:
                self.dict_states = global_mapper.map(self.dict_states, self.global_state)
            
            self.transitions_tick(submit_queue=submit_queue, results_queue=results_queue)
            
            if render: self.render(
                window=window,
                clock=clock,
                fps=render_fps,
                background=render_background
            )
        
        for i in range(0, len(workers)):
            submit_queue.put(dict(
                type=Works.EXIT
            ))