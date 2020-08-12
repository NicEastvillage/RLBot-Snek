import math
import time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.game_state_util import *
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.info import GameInfo
from util.vec import dot, Vec3, axis_to_rotation

UNLIMITED_BOOST = True
TURN_COOLDOWN = 0.25


class Snek(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.info = GameInfo(index, team)
        self.last_turn_time = 0
        self.controls = SimpleControllerState()
        self.controls.throttle = 1
        self.controls.boost = 1

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        halfpi = math.pi / 2
        car = self.info.my_car
        ball = self.info.ball
        delta_local = dot(ball.pos - car.pos, car.rot)
        ang = math.atan2(delta_local[1], delta_local[0])

        car_state = CarState()
        if UNLIMITED_BOOST:
            car_state.boost_amount = 100

        if ang > math.pi / 2 and self.last_turn_time + TURN_COOLDOWN < time.time():
            self.last_turn_time = time.time()
            mat = axis_to_rotation(Vec3(0, 0, halfpi))
            new_vel = dot(mat, car.vel)
            new_yaw = packet.game_cars[self.index].physics.rotation.yaw + halfpi
            car_state.physics = Physics(velocity=Vector3(new_vel[0], new_vel[1], new_vel[2]), rotation=Rotator(pitch=0, roll=0, yaw=new_yaw))

        if -ang > math.pi / 2 and self.last_turn_time + TURN_COOLDOWN < time.time():
            self.last_turn_time = time.time()
            mat = axis_to_rotation(Vec3(0, 0, -halfpi))
            new_vel = dot(mat, car.vel)
            new_yaw = packet.game_cars[self.index].physics.rotation.yaw - halfpi
            car_state.physics = Physics(velocity=Vector3(new_vel[0], new_vel[1], new_vel[2]), rotation=Rotator(pitch=0, roll=0, yaw=new_yaw))

        game_state = GameState(cars={self.index: car_state})
        self.set_game_state(game_state)

        return self.controls
