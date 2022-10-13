import dataclasses
from tqdm import trange
import multiprocessing

from michie.object import Object
from michie.worker import Worker

class World:
    def __init__(self, *, config=None):
        self.config = config
        self.objects = []
        self.states = []
        self.transitions = dict()
        self.transitions_ids = []
        self.window = None
        self.render_surface = None
    
    def add_object(self, *, object, init):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        state = object.state(**init)
        transitions_ids = []
        for transition in object.transitions:
            if not transition.__name__ in self.transitions:
                self.transitions[transition.__name__] = transition
            transitions_ids.append(transition.__name__)
        self.transitions_ids.append(transitions_ids)

        self.objects.append(object)
        self.states.append(state)

    def transitions_tick(self, *, submit_queue, results_queue):
        #TODO: opt-in per dataclass=>dict=>dataclass
        #      di default fare dataclass=>dict all'inizio e poi usare solo i dict
        assert submit_queue.empty() and results_queue.empty()
        dict_states = [dataclasses.asdict(state) for state in self.states]
        
        for id, (state, transitions_ids) in enumerate(zip(dict_states, self.transitions_ids)):
            submit_queue.put(["work", id, (state, transitions_ids)])
        
        updated_states = [results_queue.get() for i in range(0, len(self.objects))]
        updated_states = sorted(updated_states, key=lambda e: e[0])
        updated_states = tuple(map(lambda e: e[1], updated_states))
        self.states = [object.state(**state) for object, state in zip(self.objects, updated_states)]
        assert submit_queue.empty() and results_queue.empty()

    def render(self, *, window, background="black"):
        import pygame
        window.fill(background)
        sprites = [object.sprites for object in self.objects]
        for state, object_sprites in zip(self.states, sprites):
            for object_sprite in object_sprites: object_sprite.draw(window=window, state=state)
        pygame.display.flip()

    def run(
            self,
            *,
            workers,
            max_ticks=100,
            render=False,
            render_surface=(800, 600),
            render_background="black"
        ):   
        if render:
            import pygame
            pygame.init()
            window = pygame.display.set_mode(render_surface, pygame.HWSURFACE | pygame.DOUBLEBUF)

        submit_queue = multiprocessing.Queue()
        results_queue = multiprocessing.Queue()
        
        workers = [
            Worker(
                submit_queue=submit_queue,
                results_queue=results_queue,
                transitions=self.transitions
            ) for _ in range(0, workers)]
        [worker.start() for worker in workers]

        for i in trange(0, max_ticks):
            self.transitions_tick(submit_queue=submit_queue, results_queue=results_queue)
            if render: self.render(window=window, background=render_background)
        
        for i in range(0, len(workers)):
            submit_queue.put(["exit", None, (None, None)])