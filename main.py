from enum import  Enum
import random
import time
from multiprocessing import Process


from drawer import Drawer

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    @staticmethod
    def opposite(dir):
        if dir==Direction.UP:
            return Direction.DOWN
        if dir==Direction.RIGHT:
            return Direction.LEFT
        if dir==Direction.DOWN:
            return Direction.UP
        if dir==Direction.LEFT:
            return Direction.RIGHT

class Point:
    def __init__(self,x,y):
        self._x =x
        self._y =y

    def x(self):
        return self._x

    def y(self):
        return  self._y

    def addDirection(self,direction_other):
        if direction_other==Direction.UP:
            return Point(self._x,self._y-1)
        if direction_other==Direction.RIGHT:
            return Point(self._x+1,self._y)
        if direction_other==Direction.DOWN:
            return Point(self._x,self._y+1)
        if direction_other==Direction.LEFT:
            return Point(self._x-1,self._y)
    def __eq__(self, other):
        if other._x==self._x and self._y ==other._y:
            return True
        return False

    def __str__(self):
        return "({};{})".format(self._x,self._y)

class Labirinth:
    def __init__(self):
        self._labirynth= []

    def get_lab(self): 
        return self._labirynth

    def read_from_file(self,filename):
        self._labirynth = []
        with open(filename,"r") as f:
            for line in f:
                row= []
                for c in line.strip():
                    if c=='1':
                        row.append(None)
                    else:
                        row.append(Cfg.get_instance().pheromone_start_level)
                self._labirynth.append(row)

    def print(self):
        for row in self._labirynth:
            line=[]
            for elem in row:
                if elem is None:
                    line.append('X')
                else:
                    line.append(str(elem))
            print(''.join(line))
    def print_scale(self):
        max=0
        for row in self._labirynth:
            for elem in row:
                if elem is not None:
                    if elem > max:
                        max=elem

        for row in self._labirynth:
            line=[]
            for elem in row:
                if elem is None:
                    line.append('X')
                else:
                    line.append(str(int(elem/max*9)))
            print(''.join(line))

    def dir_list(self,pos):
        out=[]
        posUP= pos.addDirection(Direction.UP)
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

    def add_pheromone(self,pos):
        self._labirynth[pos.y()][pos.x()] += Cfg.get_instance().pheromone_add


class Cfg:
    _instance= None
    def __init__(self,anthill_pos,target_pos,pheromone_add=100.,pheromone_evaporation_amount=1.0,pheromone_start_level=0):
        self.anthill_pos=anthill_pos
        self.target_pos=target_pos
        self.pheromone_add=pheromone_add
        self.pheromone_evaporation_amount=pheromone_evaporation_amount
        self.pheromone_start_level=pheromone_start_level

    @staticmethod
    def set_instance(instance):
        Cfg._instance = instance

    @staticmethod
    def get_instance():
        return Cfg._instance




class Ant:
    def __init__(self,labirynth):
        self._path = []
        self._labirynth = labirynth
        self._pos = Cfg.get_instance().anthill_pos
        self._fsearch = True

    def move(self):
        if self._fsearch:
            return self._move_search()
        else:
            return self._move_back()

    def _move_dir(self,direction):
        if self._fsearch:
            self._path.append(Direction.opposite(direction))
        self._pos=self._pos.addDirection(direction)
        if self._pos==Cfg.get_instance().target_pos:
            self._fsearch=False

    def _move_search(self):
        dirs= self._labirynth.dir_list(self._pos)
        dirNr=random.randint(0,len(dirs)-1)
        self._move_dir(dirs[dirNr])

    def _move_back(self):
        if self._pos== Cfg.get_instance().anthill_pos:
            self._fsearch=True
            return self.move()
        self._labirynth.add_pheromone(self._pos)
        self._move_dir(self._path[-1])
        self._path = self._path[:-1]

    def print_pos(self):
        print(str(self._pos))



class AntColony:
    def __init__(self,labirynth,ants_count=15):
        self._ants_count=ants_count
        self._labirynth=labirynth
        self._ants= [ Ant(self._labirynth) for i in range(ants_count)]

    def step(self):
        for ant in self._ants:
            ant.move()
            # ant.print_pos()
            # print(ant._path)

    def stepts(self,n):
        for i in range(n):
            self.step()

    def printPos(self):
        for ant in self._ants:
            ant.print_pos()
        




if __name__=="__main__":
    Cfg.set_instance(Cfg(Point(1,1),Point(2,2)))
    lab= Labirinth()
    lab.read_from_file("exampleLab.txt")
    lab.print()
    print("")
    print("")
    print("")
    ant_colony = AntColony(lab,ants_count=20)
    ant_colony.stepts(1000)
    lab.print_scale()
    p = Process(target=Drawer.draw, args=(lab,))
    p.start()

