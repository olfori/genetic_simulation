import math
from random import randint

def get_percent(total: int | float, percent: int | float):
    """Вернет заданный процент от total"""
    return  percent * total / 100

def radius_increase(radius_absorbed, radius_absorbing):
    """Уменьшить радиус"""
    return math.sqrt(radius_absorbed**2 + radius_absorbing**2)

def get_point_polar(p: tuple | list, dist: int | float, angle_degrees: float):
    """Вернет x, y для точки удаленной от заданной p"""
    x, y = p
    x += dist * math.cos(math.radians(angle_degrees))
    y += dist * math.sin(math.radians(angle_degrees))
    return (x, y)

def compare_colors(c1, c2):
    """Сравнивает, одинаковые ли цвета"""
    return len(c1) == sum([int(c == c_) for c, c_ in zip(c1, c2)])

def mutate(value: float, min_val=0, max_val=100000, percentage=20):
    """Изменяет значение value в заданном диапазоне %, может быть ограничено min_val, max_val"""
    p_val = int(get_percent(value, percentage))
    res = value + randint(-p_val, p_val)
    if res < min_val: res = min_val
    if res > max_val: res = max_val
    return int(res)