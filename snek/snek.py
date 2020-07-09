import math
import time

from rlutilities.simulation import Game
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.game_state_util import *
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlutilities.linear_algebra import dot, axis_to_rotation, vec3

TURN_COOLDOWN = 0.25

class Snek(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.game = Game(index, team)
        self.index = index
        self.last_turn = 0
        self.controls = SimpleControllerState()
        self.controls.throttle = 1
        self.controls.boost = 1

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.game.read_game_information(packet,
                                        self.get_rigid_body_tick(),
                                        self.get_field_info())
        halfpi = math.pi / 2
        car = self.game.my_car
        ball = self.game.ball
        delta_local = dot(ball.location - car.location, car.rotation)
        ang = math.atan2(delta_local[1], delta_local[0])

        car_state = CarState(boost_amount=100)

        if ang > math.pi / 2 and self.last_turn + TURN_COOLDOWN < time.time():
            self.last_turn = time.time()
            m = axis_to_rotation(vec3(0, 0, halfpi))
            nvel = dot(m, car.velocity)
            nyaw = packet.game_cars[self.index].physics.rotation.yaw + halfpi
            car_state.physics = Physics(velocity=Vector3(nvel[0], nvel[1], nvel[2]), rotation=Rotator(pitch=0, roll=0, yaw=nyaw))

        if -ang > math.pi / 2 and self.last_turn + TURN_COOLDOWN < time.time():
            self.last_turn = time.time()
            m = axis_to_rotation(vec3(0, 0, -halfpi))
            nvel = dot(m, car.velocity)
            nyaw = packet.game_cars[self.index].physics.rotation.yaw - halfpi
            car_state.physics = Physics(velocity=Vector3(nvel[0], nvel[1], nvel[2]), rotation=Rotator(pitch=0, roll=0, yaw=nyaw))

        game_state = GameState(cars={self.index: car_state})
        self.set_game_state(game_state)

        return self.controls