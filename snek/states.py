import math
from typing import Optional

from settings import VERTICAL_TURNS
from turn import Turn
from utilities.rlmath import argmax
from utilities.vec import Vec3, normalize, dot, norm


class State:
    def exec(self, bot) -> Optional[Turn]:
        pass

    def done(self, bot) -> bool:
        pass


class GenericMoveTo(State):
    def __init__(self, target_func):
        self.target_func = target_func
        self.target: Vec3 = None

    def exec(self, bot) -> Optional[Turn]:

        self.target = self.target_func(bot)
        car = bot.info.my_car

        halfpi = math.pi / 2

        turns = [
            Turn(car.forward, None),
            Turn(car.left, car.up * halfpi),
            Turn(-car.left, car.up * -halfpi)
        ] if not VERTICAL_TURNS else [
            Turn(car.forward, None),
            Turn(car.left, car.up * halfpi),
            Turn(-car.left, car.up * -halfpi),
            Turn(car.up * 0.25, car.left * -halfpi),
            Turn(-car.up, car.left * halfpi),
        ]

        # Find best turn
        delta_n = normalize(self.target - car.pos)
        turn, _ = argmax(turns, lambda turn: dot(turn.dir, delta_n))

        return turn

    def done(self, bot) -> bool:
        return self.target is not None and norm(bot.info.my_car.pos - self.target) < 40
