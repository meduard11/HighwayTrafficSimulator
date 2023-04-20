import random
import time
from copy import deepcopy

import pygame
from road import Road
from generator import VehicleGenerator
from vehicle import checkpoint1, checkpoint2, checkpoint3, checkpoint4
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Constant that says how much self.t means 1 minute
TMIN = float(os.getenv("TMIN"))
# How much minutes between 2 data records
SAVING_DELAY = int(os.getenv("SAVING_DELAY"))
# How much time between 2 lane changing
VEHICLE_LANECHANGE_DELAY = int(os.getenv("VEHICLE_LANECHANGE_DELAY"))
# Between 0-44, the bigger it is, the more often vehicles will overtake
VEHICLE_OVERTAKE_LIMIT = int(os.getenv("VEHICLE_OVERTAKE_LIMIT"))
# Number of days we want to save data for + 1
DAY_LIMIT = int(os.getenv("DAY_LIMIT"))


class Simulation:
    def __init__(self):
        pygame.init()
        self.data_save = False
        self.screen = pygame.display.set_mode((1600, 800))
        self.clock = pygame.time.Clock()
        self.t = 0.0  # Time keeping
        self.day = 0
        self.hour = 0
        self.minutes = 0
        self.changed_hour = True
        self.changed_day = False
        self.saved_checkpoints = False
        self.insert_lane_nb = 0
        self.frame_count = 0  # Frame count keeping
        self.dt = 1 / 200  # Simulation time step
        self.roads = []  # Array to store roads
        self.generators = []
        self.checkpoints = {
            checkpoint1: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0},
            checkpoint2: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0},
            checkpoint3: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0},
            checkpoint4: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0}}
        self.data = {}
        self.stopped = False

    def save_checkpoints(self):
        self.data["day" + str(self.day) + " " + str(int(self.hour)) + ":" + str(int(self.minutes))] = [
            self.checkpoints[checkpoint1], self.checkpoints[checkpoint2], self.checkpoints[checkpoint3],
            self.checkpoints[checkpoint4]]
        # Reset values
        self.checkpoints = {
            checkpoint1: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0},
            checkpoint2: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0},
            checkpoint3: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0},
            checkpoint4: {"car": {"n": 0, "v_mean": 0, "v_total": 0}, "truck": {"n": 0, "v_mean": 0, "v_total": 0},
                          "v_total": 0, "v_mean": 0, "n": 0}}

    def save_data(self):
        df = pd.DataFrame.from_dict(self.data).transpose()
        df.to_csv('traffic.csv')

    def stop(self):
        pygame.quit()

    def create_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        return gen

    def create_road(self, start, end):
        road = Road(start, end)
        road.index = len(self.roads)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    # Adding adjccent road to each other so we can track it
    def add_adjacent_roads(self, road_idx, adj_idx):
        self.roads[road_idx].add_adjacent_road(self.roads[adj_idx])
        self.roads[adj_idx].add_adjacent_road(self.roads[road_idx])

    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt)

        # Add vehicles
        for gen in self.generators:
            gen.update()

        # Check roads for out of bounds vehicle
        for road in self.roads:
            self.update_road(road)

        # Increment time
        self.t += self.dt
        self.update_time()
        self.frame_count += 1
        # save our data
        # self.save_checkpoints()

    def update_generators(self):
        # Updating the generators so vehicle rates are changing
        for g in self.generators:
            if g.index < 23:
                g.index += 1
            else:
                g.index = 0

    def update_time(self):

        # Stops simulation and saves data when reached DAY_LIMIT
        if self.day == DAY_LIMIT and self.data_save:
            self.save_data()
            self.stopped = True

        minutes = (self.t // TMIN) % 60
        self.minutes = minutes

        # Resets the boolean for minutes
        if self.minutes % SAVING_DELAY == 1:
            self.saved_checkpoints = False

        # Reset the boolean for hours change
        if minutes == 1:
            self.changed_hour = False

        # Reset every day
        if self.hour == 1:
            self.changed_day = False

        # Saves data every SAVING_DELAY min
        if self.minutes % SAVING_DELAY == 0 and not self.saved_checkpoints and self.data_save:
            self.save_checkpoints()
            self.saved_checkpoints = True

        # Change hour
        if minutes == 59 and not self.changed_hour:
            self.hour = (self.hour + 1) % 24
            self.changed_hour = True
            self.update_generators()

        # Change day
        if self.hour == 0 and not self.changed_day:
            self.day += 1
            self.changed_day = True

    # Update each road
    def update_road(self, road):
        # If road has no vehicles, continue
        if len(road.vehicles) != 0:
            # If not we get the first vehicle
            vehicle = road.vehicles[0]

            # if vehicles reached the end of a road check if he has next road, otherwise disappear
            if vehicle.x >= road.length:
                road.vehicles.popleft()

        else:
            return

        if road.insertion:
            self.insert_road(road)

        else:
            self.normal_lane(road)
        return

    # Updates insertion lane and the lane the vehicles inserted
    def insert_road(self, road):
        # checks each vehicle on lane
        for v in list(road.vehicles):
            time_limit = 2
            max_limit = 6
            road_limit_max = 20

            # Update every checkpoint
            self.update_checkpoints(v, road)

            # Sets the insertion time
            if v.started_insertion == 0:
                v.set_started_insertion(self.t)

            elif max_limit > (self.t - v.started_insertion) > time_limit:
                v.slow(20)
            elif (self.t - v.started_insertion) > max_limit:
                v.slow(10)
                if v.x + road.start[0] > road.end[0] - road_limit_max:
                    v.slow(5)
                if v.x + road.start[0] > road.end[0] - road_limit_max - 10:
                    v.stop()

            # Calcul index road where to insert.
            next_road_index = v.current_road_index - abs(self.insert_lane_nb - road.index)

            idx = self.roads[next_road_index].check_insertion(v.x + road.start[0], road.start[0])
            if idx != -1:
                new_vehicle = deepcopy(v)
                new_vehicle.x = road.start[0] + v.x
                new_vehicle.current_road_index = next_road_index
                road.vehicles.remove(v)
                new_vehicle.last_time_lane_change = self.t
                self.roads[next_road_index].insert_vehicle_bis(new_vehicle, idx)
                new_vehicle.unslow()
                new_vehicle.unstop()

    # Update les depassements ainsi que le changement sur la voie de droite
    def normal_lane(self, road):
        # Flag to avoid double lane changing
        for v in list(road.vehicles):
            self.update_checkpoints(v, road)

            # If the vehicle recently changed his lane, do nothing, random to have non uniform delay
            if self.t - v.last_time_lane_change >= VEHICLE_LANECHANGE_DELAY - random.uniform(0, 1):

                left_lane_index = v.current_road_index - 1
                right_lane_index = v.current_road_index + 1

                # Checks if can go left and if vehicle not first of his lane
                if left_lane_index >= 0 and road.vehicles.index(v) != 0:

                    # Gets the next vehicle index on the current road
                    next_vehicle_index = road.vehicles.index(v) - 1

                    # if first vehicle of the lane, do nothing
                    if next_vehicle_index + 1 != len(road.vehicles):

                        next_vehicle = road.vehicles[next_vehicle_index]

                        next_next_vehicle = road.vehicles[next_vehicle_index + 1]

                        # Checks next vehicles speed on current lane
                        if ((next_vehicle.v < VEHICLE_OVERTAKE_LIMIT) and (
                                next_next_vehicle.v < VEHICLE_OVERTAKE_LIMIT)) or next_vehicle.v + VEHICLE_OVERTAKE_LIMIT < v.v:

                            idx = self.roads[left_lane_index].check_insertion(v.x + road.start[0],
                                                                              road.start[0], safe_distance=15)
                            if idx != -1:
                                road.vehicles.remove(v)
                                new_vehicle = deepcopy(v)
                                new_vehicle.current_road_index = left_lane_index
                                new_vehicle.last_time_lane_change = self.t
                                self.roads[left_lane_index].insert_vehicle_bis(new_vehicle, idx)

                                return

                # Check if right lane free to insert based on belgium rules
                if right_lane_index < len(self.roads) - self.insert_lane_nb:
                    idx = self.roads[right_lane_index].check_insertion(v.x + road.start[0],
                                                                       road.start[0], safe_distance=50)

                    if not self.roads[right_lane_index].insertion and idx != -1:
                        road.vehicles.remove(v)
                        new_vehicle = deepcopy(v)
                        new_vehicle.current_road_index = right_lane_index
                        new_vehicle.last_time_lane_change = self.t

                        self.roads[right_lane_index].insert_vehicle_bis(new_vehicle, idx)
                        return

    def update_checkpoints(self, v, road):
        for x_check in self.checkpoints.keys():
            if v.x + road.start[0] >= x_check and not v.checkpoints[x_check]:
                # Update number and total speed of vehicles

                self.checkpoints[x_check][v.type]["n"] += 1
                self.checkpoints[x_check][v.type]["v_total"] += v.v
                self.checkpoints[x_check][v.type]["v_mean"] = \
                    round(self.checkpoints[x_check][v.type]["v_total"] / \
                                                              self.checkpoints[x_check][v.type]["n"], 2)
                self.checkpoints[x_check]["n"] += 1
                self.checkpoints[x_check]["v_total"] += v.v
                self.checkpoints[x_check]["v_mean"] = round(self.checkpoints[x_check]["v_total"] / self.checkpoints[x_check][
                    "n"], 2)

                v.checkpoints[x_check] = 1

    def run(self, steps):
        for _ in range(steps):
            self.update()
