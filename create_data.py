import json
import os
import time
import warnings
from collections import deque
from math import gcd
from multiprocessing import Process, Queue

from ai2thor.controller import BFSController
from datasets.offline_controller_with_small_rotation import ExhaustiveBFSController


def search_and_save(in_queue):
    while not in_queue.empty():
        try:
            scene_name = in_queue.get(timeout=3)
        except:
            return
        c = None
        try:
            out_dir = os.path.join(os.path.expanduser('~/Data/Thor_offline_data_no_docker_1.0.1'), scene_name)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            print('starting:', scene_name)
            c = ExhaustiveBFSController(
                grid_size=0.25,
                fov=90.0,
                grid_file=os.path.join(out_dir, 'grid.json'),
                graph_file=os.path.join(out_dir, 'graph.json'),
                metadata_file=os.path.join(out_dir, 'metadata.json'),
                images_file=os.path.join(out_dir, 'images.hdf5'),
                depth_file=os.path.join(out_dir, 'depth.hdf5'),
                class_file=os.path.join(out_dir, 'class.json'),
                grid_assumption=False)
            # c.docker_enabled = True
            c.start()
            c.search_all_closed(scene_name)
            c.stop()
        except AssertionError as e:
            print('Error is', e)
            print('Error in scene {}'.format(scene_name))
            if c is not None:
                c.stop()
            continue


def main():
    num_processes = 20

    queue = Queue()
    scene_names = []
    for i in range(2):
        for j in range(30):
            if i == 0:
                scene_names.append("FloorPlan" + str(j + 1))
            else:
                scene_names.append("FloorPlan" + str(i + 1) + '%02d' % (j + 1))
    for x in scene_names:
        queue.put(x)

    processes = []
    for i in range(num_processes):
        p = Process(target=search_and_save, args=(queue,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == '__main__':
    main()