import math
import pygame
from pygame.locals import K_LEFT, K_RIGHT
from random import randint

from constants import *
from base import PauseMixin
from utils import *


class Circle(PauseMixin):
    """Круг, может: упираться в край экрана, управляться кнопками, измерять расстояние от центра"""
    def __init__(self, center, radius, color=RED, name='circle'):
        self.center = center
        self.init_radius = radius
        self.radius = self.init_radius
        self.color = color
        self.name = name
        self.pause = False

    def check_screen_collision(self):
        x, y = self.center
        if x <= self.radius: x = self.radius
        if x >= W - self.radius: x = W - self.radius
        if y <= self.radius: y = self.radius
        if y >= H - self.radius: y = H - self.radius
        self.center = (x, y)

    def key_control(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.direction -= ANIMAL_TURNING_SPEED
        if pressed_keys[K_RIGHT]:
            self.direction += ANIMAL_TURNING_SPEED

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.center, self.radius, 2)

    def dist(self, point):
        return math.dist(point, self.center)

    def xydist(self, x, y):
        x1, y1 = self.center
        dist = self.dist(x, y)
        return x1, y1, dist
    
    def __str__(self):
        self.name
    
    def __repr__(self):
        self.name


class Food(Circle):
    """Еда: может расти, иметь лепестки"""
    def __init__(self, center, radius=2, color=GREEN):
        super().__init__(center, radius, color)
        self.start_angle = randint(-FOOD_START_ANGLE, FOOD_START_ANGLE)

    def growth(self):
        if self.radius < FOOD_MAX_RADIUS and not self.pause:
            self.radius += FOOD_GROWTH_RATE * APP_SPEED
    
    def draw_petals(self, surface):
        r = self.radius
        alpha = 360 / FOOD_PETALS_COUNT
        for i in range(FOOD_PETALS_COUNT):
            center = get_point_polar(self.center, r/1.5, self.start_angle + i * alpha)
            pygame.draw.circle(surface, self.color, center, r/2, 2)

    def draw(self, surface):
        r = self.radius
        pygame.draw.circle(surface, self.color, self.center, r, 2)
        if FOOD_SHOW_PETAILS:
            self.draw_petals(surface)
            pygame.draw.circle(surface, self.color, self.center, r/2, 2)

    def update(self, surface):
        self.check_screen_collision()
        self.growth()
        self.draw(surface)


class Animal(Circle):
    def __init__(
            self,
            center,
            radius=ANIMAL_INIT_RADIUS,
            color=BLUE,
            init_life_time=ANIMAL_LIFE_TIME,
            max_radius=ANIMAL_MAX_RADIUS,
            sight_distance=ANIMAL_SIGHT_DISTANCE,
        ):
        super().__init__(center, radius, color)
        self.speed = ANIMAL_INIT_SPEED
        self.weight_loss = ANIMAL_WEIGHT_LOSS
        self.max_radius = max_radius
        self.init_sight_distance = sight_distance
        self.sight_distance = self.init_sight_distance
        self.init_life_time = init_life_time
        self.life_time = self.init_life_time
        self.eys_angle = ANIMAL_EYS_ANGLE + randint(-20, 20)
        self.direction = 0
        self.curr_direction = 0
        self.target = None
        self.is_predator = True
        self.trajectory_color = (randint(0,255), randint(0,255), randint(0,255))
        self.rapacity = randint(0,100) # хищность в %


    def update_params(self):
        if self.radius > 10:
            self.speed = (20 / self.radius) * APP_SPEED
        elif self.radius > 5:
            self.speed = (10 / self.radius) * APP_SPEED
        else:
            self.speed = (5 / self.radius) * APP_SPEED

    def update_life_time(self):
        self.life_time -= 1

    def step(self):
        if not self.pause:
            # Логика с поворотом
            self.curr_direction %= 360
            if (self.direction - 1)%360 <= self.curr_direction <= (self.direction + 1)%360:
                x, y = self.center
                x += self.speed * math.cos(math.radians(self.direction))
                y += self.speed * math.sin(math.radians(self.direction))
                self.center = (x, y)
                return
            if (self.curr_direction - self.direction)%360 >= (self.curr_direction + self.direction)%360:
                self.curr_direction += ANIMAL_TURNING_SPEED
            else:
                self.curr_direction -= ANIMAL_TURNING_SPEED

            x, y = self.center
            x += self.speed * math.cos(math.radians(self.direction))
            y += self.speed * math.sin(math.radians(self.direction))
            self.center = (x, y)

    def draw_a_trajectory(self, surface):
        x, y = self.center
        x, y = int(x), int(y)
        r = self.radius / 4 or 1
        # surface.set_at((x, y), self.color) # Рисует точками
        pygame.draw.circle(surface, self.trajectory_color, (x, y), r) #  Рисует круги (более насыщено)

    def calc_weight(self):
        if not self.pause:
            self.radius -= self.weight_loss * APP_SPEED

    def collide(self, animals):
        for other in filter(lambda a: a != self, animals):
            if self.dist(other.center) < self.radius + other.radius:
                self._resolve_collision(other)

    def _resolve_collision(self, other):
        x, y = self.center
        ax, ay = other.center
        angle = math.atan2(ay - y, ax - x)
        other.center = (
            ax + other.speed * math.cos(angle),
            ay + other.speed * math.sin(angle),
        )
        if self.radius > other.radius:
            if compare_colors(self.color, other.color):
                # Одноцветные: большие отдают массу маленьким
                # self.radius -= self.weight_loss*100
                # a.radius += a.weight_loss*100
                pass
            # большие забирают массу у маленьких
            self.radius += self.weight_loss * 100
            other.radius -= self.weight_loss * 100

    def set_rand_direction(self):
        rd = ANIMAL_RAND_DIRECTION
        self.direction += randint(-rd, rd)

    def check_target(self, food_list):
        if self.target not in food_list:
            self.target = None

    def set_target(self, target):
        x, y = self.center
        tx, ty = target.center
        self.direction = int(math.degrees(math.atan2(ty - y, tx - x)))
        self.target = target
        target.color = YELLOW

    def select_food(self, food_list):
        if not self.target:
            self.set_rand_direction()
            visible_food = list(filter(lambda f: f.dist(self.center) < self.sight_distance, food_list))
            if not visible_food:
                return
            visible_food.sort(key=lambda f: f.dist(self.center))
            self.set_target(visible_food[0])
    
    def eat_food(self, food_list):
        for f in food_list:
            if f.dist(self.center) < self.radius < self.max_radius:
                food_list.remove(f)
                self.radius = radius_increase(self.radius, f.radius)

    def watch_around(self, food_list):
        self.check_target(food_list)
        self.select_food(food_list)
        self.eat_food(food_list)
        self.direction %= 360

    def check_if_dead(self, animals, natural_death, died_violently, food_list):
        if self.radius < ANIMAL_MIN_RADIUS:
            animals.remove(self)
            died_violently += 1
        elif self.life_time <= 0:
            animals.remove(self)
            natural_death += 1
            self._spawn_food(food_list)
        return natural_death, died_violently
    
    def _spawn_food(self, food_list):
        for _ in range(int(self.radius)):
            x, y = self.center
            r = int(self.radius)
            food_center = x + randint(-r, r), y + randint(-r, r)
            food_list.append(Food(food_center))

    def draw(self, surface):
        super().draw(surface)
        self._draw_nose(surface)
        self._draw_eys(surface)

    def _draw_nose(self, surface):
        if self.target:
            r, d = self.radius, self.direction
            p1 = get_point_polar(self.center, r, d)
            p2 = get_point_polar(p1, r/5, d)
            pygame.draw.line(surface, self.color, p2, p1, 2)
    
    def _draw_eys(self, surface):
        r, d = self.radius, self.direction
        p1 = get_point_polar(self.center, r/2, d + self.eys_angle)
        p2 = get_point_polar(self.center, r/2, d - self.eys_angle)
        pygame.draw.circle(surface, self.color, p1, r/4, 1)
        pygame.draw.circle(surface, self.color, p1, 1)
        pygame.draw.circle(surface, self.color, p2, r/4, 1)
        pygame.draw.circle(surface, self.color, p2, 1)

    def update(self, surface):
        self.check_screen_collision()
        self.update_life_time()
        self.step()
        self.calc_weight()
        self.update_params()
        self.draw(surface)

    def check_if_child_was_born(self, obj_list):
        if self.radius >= self.max_radius:
            cr = mutate(self.init_radius, 5, self.radius/2)
            r = radius_increase(self.radius, cr)
            child_center = get_point_polar(self.center, r, (self.direction-180)%360)
            child = Animal(
                center=child_center,
                radius=cr,
                color=self.color,
                init_life_time=mutate(self.init_life_time, 100, 10000),
                max_radius=mutate(self.max_radius, 10, 50),
                sight_distance=mutate(self.init_sight_distance, 5, 400),
            )
            self.radius -= child.radius
            obj_list.append(child)

    def show_info(self, mouse_coordinates, render_text_fnc):
        if self.dist(mouse_coordinates) < self.radius:
            x, y = self.center
            font_size = 15
            r = self.radius + font_size
            render_text_fnc(
                f'{self.init_life_time} {self.init_radius} {self.max_radius} {self.init_sight_distance}',
                x-r/2,
                y-r
            )