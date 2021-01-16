import math
import time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.game_state_util import *
from rlbot.utils.structures.game_data_struct import GameTickPacket

from settings import ARTIFICIAL_UNLIMITED_BOOST, TURN_COOLDOWN
from states import GenericMoveTo
from utilities.info import GameInfo
from utilities.vec import dot, axis_to_rotation, rotation_to_euler, normalize, looking_in_dir, xy


class SnekPro(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.info = GameInfo(index, team)
        self.last_turn_time = 0
        self.controls = SimpleControllerState()
        self.controls.throttle = 1
        self.controls.boost = 1
        self.state = GenericMoveTo(lambda bot: bot.info.ball.pos + normalize(self.info.opp_goal.pos - bot.info.ball.pos) * -60)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        car = self.info.my_car
        ball = self.info.ball

        car_state = CarState()
        if ARTIFICIAL_UNLIMITED_BOOST:
            car_state.boost_amount = 100

        if ball.pos.x == 0 and ball.pos.y == 0:
            # Kickoff
            self.last_turn_time = time.time()
            euler = rotation_to_euler(looking_in_dir(xy(ball.pos - car.pos)))
            car_state.physics = Physics(
                rotation=Rotator(pitch=euler.x, roll=0, yaw=euler.y)
            )

        elif self.last_turn_time + TURN_COOLDOWN < time.time():

            self.choose_state()
            turn = self.state.exec(self)

            if turn is not None and turn.axis is not None:
                self.last_turn_time = time.time()
                mat = axis_to_rotation(turn.axis)
                new_vel = dot(mat, car.vel)
                new_rot = dot(mat, car.rot)
                euler = rotation_to_euler(new_rot)
                car_state.physics = Physics(
                    velocity=Vector3(new_vel[0], new_vel[1], new_vel[2]),
                    rotation=Rotator(pitch=euler.x, roll=0, yaw=euler.y)
                )

        game_state = GameState(cars={self.index: car_state})
        self.set_game_state(game_state)

        return self.controls

    def choose_state(self):
        pass
