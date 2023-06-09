from vehicle import Vehicle
from numpy.random import randint
import random

RANDOM_BETA = 5

class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim
        self.beta = 1
        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.vehicle_rate = [20, 20, 20]
        self.vehicles = [
            (1, {})
        ]
        self.last_added_time = 0
        self.index = 0
        self.vehicles_stock = []
        # tendance des voitures

    def init_properties(self):
        self.upcoming_vehicle = self.generate_vehicle()
        self.vehicles_stock.append(self.upcoming_vehicle)

    def generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        total = sum(pair[0] for pair in self.vehicles)
        r = randint(1, total + 1)
        for (weight, config) in self.vehicles:
            r -= weight
            if r <= 0:
                return Vehicle(config)

    def update(self):

        bruit = (self.vehicle_rate[self.index] * self.beta) / 10
        random_bruit = random.uniform(0, bruit * 2)
        v_rate = (self.vehicle_rate[self.index] * self.beta) - bruit + random_bruit

        # Un véhicule apparait toutes les 60/self.rate sec, self_rate = 60 -> 1 véhicule par seconde, par generateur
        if self.sim.t - self.last_added_time >= 60 / v_rate:
            # randomly cancel vehicle spawn and spawn +1 as much on next iteration if canceled
            random_gen = random.randint(1, RANDOM_BETA)
            if random_gen == RANDOM_BETA:
                self.beta += 1
                return
            # If time elasped after last added vehicle is
            # greater than vehicle_period; generate a vehicle
            road = self.sim.roads[self.upcoming_vehicle.path[0]]
            if len(road.vehicles) == 0 \
                    or road.vehicles[-1].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:
                # If there is space for the generated vehicle; add it
                self.upcoming_vehicle.time_added = self.sim.t
                self.upcoming_vehicle.position = len(road.vehicles)
                self.upcoming_vehicle.timeline = self.sim.t
                road.vehicles.append(self.upcoming_vehicle)
                self.beta = 1
                # Reset last_added_time and upcoming_vehicle
                self.last_added_time = self.sim.t
            self.upcoming_vehicle = self.generate_vehicle()
