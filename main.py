from random import randint
import pygame

from constants import *
from base import PauseMixin, ChartData, Counter
from entities import Food, Animal


class PygameApp(PauseMixin):
    def __init__(self):
        pygame.font.init()
        pygame.init()
        pygame.display.set_caption("Game1")
        self.bg = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 12)
        self.running = True
        self.pause = False
        self.mouse_coordinates = None
        self.show_trajectory = False
 
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONUP:
                self.toggle_pause()
            if event.type == pygame.KEYDOWN:
                self.show_trajectory = not self.show_trajectory
        self.mouse_coordinates = pygame.mouse.get_pos()

    def render_text(self, text, x=0, y=10):
        text = f'{text}'
        self.bg.blit(self.font.render(text, -1, BLACK),(x, y))

    def render(self):
        self.render_text(f'Для запуска игры, реализуйте метод render класса PygameApp')

    def run(self):
        while self.running:
            self.process_events()
            self.bg.fill(WHITE)

            self.render()

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()


class AnimalsGame():
    def __init__(self):
        self.pygame_app = PygameApp()
        self.chart = pygame.Surface((W, H))
        self.chart.set_alpha(200)

        self.trajectory = pygame.Surface((W, H))
        self.trajectory.set_alpha(200)
        self.fade_trajectory_timer = Counter(3, self.fade_trajectory)

        self.food_counter = Counter(5, self.add_food)
        self.chart_counter = Counter(100)
        self.food_list = []
        self.animals = []
        self.natural_death = 0
        self.died_violently = 0
        self.chart_data = ChartData()

    def init_animals(self):
        c1 = Animal((ANIMAL_INIT_XY, ANIMAL_INIT_XY))
        c2 = Animal((W - ANIMAL_INIT_XY, H - ANIMAL_INIT_XY), color=RED)
        self.animals = [c1, c2]

    def add_food(self):
        for _ in range(APP_FOOD_AT_A_TIME):
            d = SCREEN_EDGE_DISTANCE
            p = (randint(d, W - d), randint(d, H - d))
            self.food_list.append(Food(p))

    def food_step(self):
        if len(self.food_list) < APP_MAX_FOOD and not self.pygame_app.pause:
            self.food_counter.step()

    def update_food(self):
        for obj in self.food_list:
            obj.update(self.pygame_app.bg)
            obj.set_pause(self.pygame_app.pause)

    def update_animals(self):
        for obj in self.animals:
            obj.set_pause(self.pygame_app.pause)
            obj.collide(self.animals)
            obj.update(self.pygame_app.bg)
            obj.watch_around(self.food_list, self.animals)
            self.natural_death, self.died_violently = obj.check_if_dead(
                self.animals, self.natural_death, self.died_violently, self.food_list
            )
            obj.check_if_child_was_born(self.animals)
            obj.show_info(
                self.pygame_app.mouse_coordinates,
                self.pygame_app.render_text
            )
            obj.draw_a_trajectory(self.trajectory)

    def add_chart_data(self):
        a_count = len(self.animals)
        if not a_count:
            return
        i = self.chart_counter.total
        try:
            mn, mx = self.chart_data.animals_count[i]
            self.chart_data.animals_count[i] = [min(a_count, mn), max(a_count, mx)]
        except Exception as e:
            self.chart_data.animals_count.append([a_count, a_count])
        
        lt_min = min(self.animals, key=lambda a: a.init_life_time).init_life_time
        lt_max = max(self.animals, key=lambda a: a.init_life_time).init_life_time
        try:
            mn, mx = self.chart_data.life_time[i]
            self.chart_data.life_time[i] = [min(lt_min, mn), max(lt_max, mx)]
        except Exception as e:
            self.chart_data.life_time.append([lt_min, lt_max])


    def process_chart_counter(self):
        self.chart_counter.step()
        self.chart_counter.set_pause(self.pygame_app.pause)
        self.add_chart_data()

    def show_chart(self):
        self.chart.fill(WHITE)
        for x, d in enumerate(self.chart_data.animals_count):
            mn, mx = d
            p1, p2 = (x*2, H - mn), (x*2, H - mx)
            pygame.draw.line(self.chart, BLUE, p2, p1, 1)

            mn, mx = self.chart_data.life_time[x]
            divider, h = 50, 80
            p1, p2 = (x*2, H - mn/divider - h), (x*2, H - mx/divider - h)
            pygame.draw.line(self.chart, GREEN, p2, p1, 1)
        self.pygame_app.bg.blit(self.chart, (0, 0))

    def show_trajectory(self):
        self.pygame_app.bg.blit(self.trajectory, (0, 0))

    def fade_trajectory(self):
        fade_surface = pygame.Surface(self.trajectory.get_size(), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 5))  # Заливка с небольшим уровнем альфа для затухания
        self.trajectory.blit(fade_surface, (0, 0))

    def render(self):
        self.process_chart_counter()
        self.food_step()
        self.update_food()
        self.update_animals()
        la, nd, dv = len(self.animals), self.natural_death, self.died_violently
        self.pygame_app.render_text(
            f'All:{la} Dead:+{nd} -{dv} Еды:{len(self.food_list)}'
        )
        if self.pygame_app.pause:
            self.show_chart()
        self.fade_trajectory_timer.step()
        if self.pygame_app.show_trajectory:
            self.show_trajectory()

    def run(self):
        self.pygame_app.render = self.render
        self.init_animals()
        self.pygame_app.run()

 
if __name__ == "__main__" :
    app = AnimalsGame()
    app.run()

