from scipy.spatial import distance
from collections import deque
from datetime import datetime, timedelta


class Road():
    def __init__(self, start, end, adj_roads=None, insertion=False):

        if adj_roads is None:
            adj_roads = []

        self.start = start
        self.end = end
        self.adj_roads = adj_roads
        self.vehicles = deque()
        self.insertion = insertion
        self.vehicles_nb = 0
        self.init_properties()

    def init_properties(self):
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1] - self.start[1]) / self.length
        self.angle_cos = (self.end[0] - self.start[0]) / self.length
        # self.angle = np.arctan2(self.end[1]-self.start[1], self.end[0]-self.start[0])

    def update(self, dt):
        n = len(self.vehicles)
        if n > 0:
            # Update first vehicle
            self.vehicles[0].update(None, dt)
            # Update other vehicles

            for i in range(1, n):
                lead = self.vehicles[i - 1]
                self.vehicles[i].update(lead, dt)

    def add_adjacent_road(self, road):
        self.adj_roads.append(road)

    def set_insertion(self, ins):
        self.insertion = ins

    # Returns index where can be inserted, -2 for appendLeft, -1 for no insert or i
    def check_insertion(self, x, prevStart, safe_distance=10):
        min_dist = 30

        if x > min_dist + prevStart:
            # If no vehicle on the road, we can insert
            if len(self.vehicles) < 1:
                return -2

            # If only 1 car on next lane, don't need to check more
            if len(self.vehicles) == 1 and (self.vehicles[0].x + safe_distance < x or self.vehicles[0].x - safe_distance > x):
                return -2

            # Checks first car of list and append if far enough
            if self.vehicles[0].x + safe_distance < x:
                return -2

            # Finds the index of the previous car
            i = 0
            for v in self.vehicles:
                if v.x < x:
                    break
                i += 1

            # if i corresponds to the number of cars on the road, we can deduct no place was found
            if len(self.vehicles) == i:
                return -1

            if self.vehicles[i - 1].x - safe_distance > x > self.vehicles[i].x + safe_distance:
                return i
        return -1

    def insert_vehicle_bis(self, vehicule, index):
        if index == -2:
            self.vehicles.appendleft(vehicule)
        else:
            self.vehicles.insert(index, vehicule)

    # Inserts the vehicle on the next path
    def insert_vehicle(self, vehicule, prevStart, safe_distance=10):

        min_dist = 30

        if vehicule.last_time_lane_change == 0:
            vehicule.last_time_lane_change = datetime.now()
        elif datetime.now() - vehicule.last_time_lane_change < timedelta(seconds=1):
            return False

        if vehicule.x > min_dist + prevStart:

            # If no vehicle on the road, we can insert
            if len(self.vehicles) < 1:
                self.vehicles.appendleft(vehicule)
                return True

            # If only 1 car on next lane, don't need to check more
            if len(self.vehicles) == 1 and self.vehicles[0].x + safe_distance < vehicule.x:
                self.vehicles.appendleft(vehicule)
                return True

            # Checks first car of list and append if far enough
            if self.vehicles[0].x + safe_distance < vehicule.x:
                self.vehicles.appendleft(vehicule)
                return True

            # Finds the index of the previous car
            i = 0
            for v in self.vehicles:
                if v.x < vehicule.x:
                    break
                i += 1

            # if i corresponds to the number of cars on the road, we can deduct no place was found
            if len(self.vehicles) == i:
                return False

            if self.vehicles[i - 1].x - safe_distance > vehicule.x > self.vehicles[i].x + safe_distance:
                self.vehicles.insert(i, vehicule)
                return True

        return False
