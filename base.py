class PauseMixin:
    """Миксин для добавления обьекту паузы"""
    def set_pause(self, pause):
        self.pause = pause

    def toggle_pause(self):
        self.pause = not self.pause


class ChartData():
    def __init__(self):
        self.animals_count = []
        self.life_time = []


class Counter(PauseMixin):
    """Счетчик, когда доходит до max_tick, запускается func"""
    def __init__(self, max_tick, func=None):
        self.count = 0
        self.total = 0
        self.max_tick = max_tick
        self.func = func
        self.pause = False

    def step(self):
        if not self.pause:
            if self.count < self.max_tick:
                self.count += 1
            else:
                self.total += 1
                self.count = 0
                if self.func: self.func()