import sys

from simulation import Simulation
from window import Window
import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VR = float(os.getenv("ALPHA_VR"))


TREND = [2, 4, 2, 2, 5, 8, 14, 19, 15, 12, 8, 6, 6, 5, 7, 10, 15, 20, 15, 10, 6, 4, 5, 3]

mode = int(sys.argv[1])

sim = Simulation()

# !!!Insertion roads have to be at the end of our list
sim.create_roads(
    [
        ((0, 10), (2000, 10)),
        ((0, 14), (2000, 14)),
        ((0, 18), (2000, 18)),
        ((200, 22), (500, 22)),
        ((800, 22), (1100, 22))
    ]
)

adjacent_roads = [(0, 1), (1, 2), (2, 3)]

# defining the 3rd and 4th road as an insertion lane
sim.roads[3].set_insertion(True)
sim.insert_lane_nb += 1
sim.roads[4].set_insertion(True)
sim.insert_lane_nb += 1


# adding adjacent roads to each other
for adj in adjacent_roads:
    sim.add_adjacent_roads(adj[0], adj[1])

sim.create_gen({
    'vehicle_rate': [i * ALPHA_VR * 2 for i in TREND],
    'index': 0,
    'vehicles': [
        [1, {'path': [0]}],
        [1, {'path': [0]}],
        [1, {'path': [0]}],

        [1, {'path': [1, 0]}],
        [1, {'path': [1, 0]}],
        [1, {'path': [1, 0]}],

        [1, {'path': [2, 1]}],
        [1, {'path': [2, 1]}],
        [1, {'path': [2, 1]}],
    ]})

sim.create_gen(
    {
        'vehicle_rate':  [i * ALPHA_VR for i in TREND],
        'index': 0,
        'vehicles': [
            [1, {'path': [3, 2]}]]
    })


sim.create_gen(
        {
            'vehicle_rate': [i * ALPHA_VR for i in TREND],
            'index': 0,
            'vehicles': [
                [1, {'path': [4, 2]}]]
        })

if mode == 0:
    print("Starting simulation mode")
    sim.data_save = True

    win = Window(sim)
    win.zoom = 2
    win.run(steps_per_update=10)

else:
    print("Starting non graphic mode and saving data")
    sim.data_save = True
    while True and not sim.stopped:
        sim.run(10)
