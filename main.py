from enum import Enum
import random
import time
from multiprocessing import Process
import numpy as np
from numpy.random import choice as np_choice
import _thread
import argparse

parser = argparse.ArgumentParser(description='find way in labirynth !')
parser.add_argument('-x1',dest='x1', default=1, type=int, help='x coordinate of first point')
parser.add_argument('-y1',dest='y1', default=1, type=int, help='y coordinate of first point')
parser.add_argument('-x2',dest='x2', default=14, type=int, help='x coordinate of second  point')
parser.add_argument('-y2',dest='y2', default=14, type=int, help='y coordinate of second point')
parser.add_argument('-ps',dest='pheromone_start', type=float, default=0, help='starting level of pheromone')
parser.add_argument('-pe',dest='pheromone_evaporation', type=float, default=2.0, help='how much pheromone evaportes with each step')
parser.add_argument('-pa',dest='pheromone_ad', type=float, default=100., help='how much pheromone add with each step')
parser.add_argument('-f',dest='file_name', type=str, default='')


from drawer import Drawer


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    @staticmethod
    def opposite(dir):
        if dir == Direction.UP:
            return Direction.DOWN
        if dir == Direction.RIGHT:
            return Direction.LEFT
        if dir == Direction.DOWN:
            return Direction.UP
        if dir == Direction.LEFT:
            return Direction.RIGHT


class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def addDirection(self, direction_other):
        if direction_other == Direction.UP:
            return Point(self._x, self._y-1)
        if direction_other == Direction.RIGHT:
            return Point(self._x+1, self._y)
        if direction_other == Direction.DOWN:
            return Point(self._x, self._y+1)
        if direction_other == Direction.LEFT:
            return Point(self._x-1, self._y)

    def __eq__(self, other):
        if other._x == self._x and self._y == other._y:
            return True
        return False

    def __str__(self):
        return "({};{})".format(self._x, self._y)


class Labirinth:
    def __init__(self):
        self._labirynth = []

    def get_lab(self):
        return self._labirynth

    def read_from_file(self, filename):
        self._labirynth = []
        with open(filename, "r") as f:
            for line in f:
                row = []
                for c in line.strip():
                    if c == '1':
                        row.append(None)
                    else:
                        row.append(Cfg.get_instance().pheromone_start_level)
                self._labirynth.append(row)

    def print(self):
        for row in self._labirynth:
            line = []
            for elem in row:
                if elem is None:
                    line.append('X')
                else:
                    line.append(str(elem))
            print(''.join(line))

    def find_max_pheromon(self):
        max = 0
        for row in self._labirynth:
            for elem in row:
                if elem is not None:
                    if elem > max:
                        max = elem
        return max

    def print_scale(self):
        max = self.find_max_pheromon()
        for row in self._labirynth:
            line = []
            for elem in row:
                if elem is None:
                    line.append('X')
                else:
                    line.append(str(int(elem/max*9)))
            print(''.join(line))

    def dir_list(self, pos):
        out = []
        posUP = pos.addDirection(Direction.UP)
        if self._labirynth[posUP.y()][posUP.x()] is not None:
            out.append(Direction.UP)
        posRIGHT = pos.addDirection(Direction.RIGHT)
        if self._labirynth[posRIGHT.y()][posRIGHT.x()] is not None:
            out.append(Direction.RIGHT)
        posDOWN = pos.addDirection(Direction.DOWN)
        if self._labirynth[posDOWN.y()][posDOWN.x()] is not None:
            out.append(Direction.DOWN)
        posLEFT = pos.addDirection(Direction.LEFT)
        if self._labirynth[posLEFT.y()][posLEFT.x()] is not None:
            out.append(Direction.LEFT)
        return out

    def neigbour_fields(self, pos):
        out = []
        posUP = pos.addDirection(Direction.UP)
        if self._labirynth[posUP.y()][posUP.x()] is not None:
            out.append(posUP)
        posRIGHT = pos.addDirection(Direction.RIGHT)
        if self._labirynth[posRIGHT.y()][posRIGHT.x()] is not None:
            out.append(posRIGHT)
        posDOWN = pos.addDirection(Direction.DOWN)
        if self._labirynth[posDOWN.y()][posDOWN.x()] is not None:
            out.append(posDOWN)
        posLEFT = pos.addDirection(Direction.LEFT)
        if self._labirynth[posLEFT.y()][posLEFT.x()] is not None:
            out.append(posLEFT)
        return out

    def add_pheromone(self, pos):
        self._labirynth[pos.y()][pos.x()] += Cfg.get_instance().pheromone_add


class Cfg:
    _instance = None

    def __init__(self, anthill_pos, target_pos, pheromone_add=100., pheromone_evaporation_amount=2.0, pheromone_start_level=0):
        self.anthill_pos = anthill_pos
        self.target_pos = target_pos
        self.pheromone_add = pheromone_add
        self.pheromone_evaporation_amount = pheromone_evaporation_amount
        self.pheromone_start_level = pheromone_start_level

    @staticmethod
    def set_instance(instance):
        Cfg._instance = instance

    @staticmethod
    def get_instance():
        return Cfg._instance


class Ant:
    def __init__(self, labirynth):
        self._path = []
        self._labirynth = labirynth
        self._pos = Cfg.get_instance().anthill_pos
        self._fsearch = True

    def move(self):
        if self._fsearch:
            return self._move_search()
        else:
            return self._move_back()

    def _move_dir(self, direction):
        if self._fsearch:
            self._path.append(Direction.opposite(direction))
        self._pos = self._pos.addDirection(direction)
        if self._pos == Cfg.get_instance().target_pos:
            self._fsearch = False

    def _move_search(self):
        self._move_dir(self._chose_path())

    def _move_back(self):
        if self._pos == Cfg.get_instance().anthill_pos:
            self._fsearch = True
            return self.move()
        self._labirynth.add_pheromone(self._pos)
        self._move_dir(self._path[-1])
        self._path = self._path[:-1]

    def print_pos(self):
        print(str(self._pos))

    def _chose_path(self):
        dirs = self._labirynth.dir_list(self._pos)
        neigbour_fields = self._labirynth.neigbour_fields(self._pos)
        neigbour_fields_probability = [((self._labirynth._labirynth[pos.y()][pos.x(
        )]+1))/(self._labirynth.find_max_pheromon()+1) for pos in neigbour_fields]
        neigbour_fields_probability_with_adjusted_p = [
            prob/sum(neigbour_fields_probability) for prob in neigbour_fields_probability]
        return np_choice(dirs, p=neigbour_fields_probability_with_adjusted_p)


class AntColony:
    def __init__(self, labirynth, ants_count=15):
        self._ants_count = ants_count
        self._labirynth = labirynth
        self._ants = [Ant(self._labirynth) for i in range(ants_count)]

    def step(self):
        for ant in self._ants:
            ant.move()
            # ant.print_pos()
            # print(ant._path)
        for row in self._labirynth.get_lab():
            for element in row:
                if element is not None:
                    if element > Cfg.get_instance().pheromone_evaporation_amount:
                        element -= Cfg.get_instance().pheromone_evaporation_amount
                    else:
                        element=0

    def stepts(self, n):
        for i in range(n):
            self.step()

    def printPos(self):
        for ant in self._ants:
            ant.print_pos()


if __name__ == "__main__":
    Cfg.set_instance(Cfg(Point(1, 1), Point(14, 14)))
    lab = Labirinth()
    lab.read_from_file("exampleLab.txt")
    lab.print()
    print("")
    print("")
    print("")
    ant_colony = AntColony(lab, ants_count=20)
    _thread.start_new_thread(Drawer.draw,(lab,Cfg.get_instance()))
    while True:
        # time.sleep(0.1)
        ant_colony.stepts(50000000)


