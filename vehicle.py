import random

import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# Car longueur
L = int(os.getenv("L"))
# Space between next car
S0 = int(os.getenv("S0"))
# Reaction time
T = int(os.getenv("T"))
# Vitesse max d'un véhicule qui varie entre V_MAX1 et V_MAX2 (en m/s)
V_MAX1, V_MAX2 = float(os.getenv("V_MAX1")), float(os.getenv("V_MAX2"))
# Acceleration max d'un véhicule qui varie entre A_MAX1 et A_MAX2 (en m/s^^2)
A_MAX1, A_MAX2 = float(os.getenv("A_MAX1")), float(os.getenv("A_MAX2"))
# Deceleration max d'un véhicule qui varie entre B_MAX1 et B_MAX2 (en m/s^^2)
B_MAX1, B_MAX2 = float(os.getenv("B_MAX1")), float(os.getenv("B_MAX2"))
# 1/TRUCK_RATE will be a truck
TRUCK_RATE = int(os.getenv("TRUCK_RATE"))
# Same goes for motorcycles
MOTOR_RATE = int(os.getenv("MOTOR_RATE"))

checkpoint1 = int(os.getenv("CHECKPOINT1"))
checkpoint2 = int(os.getenv("CHECKPOINT2"))
checkpoint3 = int(os.getenv("CHECKPOINT3"))
checkpoint4 = int(os.getenv("CHECKPOINT4"))


class Vehicle:
    def __init__(self, config={}):
        self.type = "car"  # Or "Truck" or "Motorcycle"
        self.checkpoints = {checkpoint1: False, checkpoint2: False, checkpoint3: False, checkpoint4: False}
        self.last_time_lane_change = 0
        self.started_insertion = 0
        self.position = 0
        self.stopped = False
        self.a = 0
        self.x = 0
        self.adj = []
        self.path = []
        self.b_max = random.uniform(B_MAX1, B_MAX2)
        self.a_max = random.uniform(A_MAX1, A_MAX2)
        self.v_max = random.uniform(V_MAX1, V_MAX2)
        self.v = self.v_max
        self.T = T
        self.s0 = S0
        self.timeline = 0
        self.l = L
        self.h = 2
        self.color = (0, 0, 255)
        # Calculate properties
        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)
        self._v_max = self.v_max

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

        self.current_road_index = self.path[0]

        self.init_type()

    # Generates buses and motorcycles
    def init_type(self):
        # Generate randomly bus
        random_number = random.randint(1, TRUCK_RATE)
        if random_number == TRUCK_RATE:
            self.type = "truck"
            self.l = 8
            self.a_max = 1.2
            self.v_max = 18
            self.color = (255, 0, 0)
            return
        random_number = random.randint(1, MOTOR_RATE)
        if random_number == MOTOR_RATE:
            self.l = 3
            self.h = 1
            self.a_max = 4
            self.v_max = 48
            self.color = (255,255,0)

    def set_started_insertion(self, time):
        self.started_insertion = time

    # dt correspond aux fps qu'on désire avoir
    def update(self, lead, dt):

        # Update position and velocity
        if self.v + self.a * dt < 0:
            self.x -= 1 / 2 * self.v * self.v / self.a
            self.v = 0
        else:
            self.v += self.a * dt
            self.x += self.v * dt + self.a * dt * dt / 2

        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.l
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T * self.v + delta_v * self.v / self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1 - (self.v / self.v_max) ** 4 - alpha ** 2)

        if self.stopped:
            self.a = -self.b_max * self.v / self.v_max

    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max

    def set_pos(self, position):
        self.position = position
