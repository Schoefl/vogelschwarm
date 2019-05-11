## idee: klasse Schwarmmitglied oder so, die globale Variablen ernthaelt und klasse bird erbt?
# bzw ein schwarm ist eine Klasse, in der alle birds abgespeichert werden, schwarm bekommt als Parameter 
# ob bird oder fish

import numpy as np
from matplotlib import pyplot as plt
import sys
import time 

## in python 2, classes work differently (must inherite object in our case)
if sys.version_info[0] < 3:
    raise Exception("Python 3 is required, you are using ",
     sys.version_info[0])


class Swarm:
    ## ToDo: messing with the __new()__ to ensure, no individuals
    ## are created outside of swarm's create indiviadual's method
    ## ToDo: allow birds to fly out of space

    ## ToDo: create methods to change 'changeable parameters'
    def __init__(self, amount_of_individuals=50):
        self.__amount_of_individuals = amount_of_individuals

        ## changeable parameters
        self._fs = 1                      # field size [0,_fs]x[0,_fs]
        self._vel = 0.01*self._fs          # velocity 
        self._radius_sep = 0.1*self._fs   # radius for seperation 0.03
        self._radius_ali = 0.2*self._fs    # radius for alignment 0.05
        self._radius_co  = self._fs    # radius for cohesion 0.15
        self._weight_ali = 0.2          # weight for alignment
        self._weight_co  = 0.9         # weight for cohesion
        self._pause = 0.01           # pause between steps

        ## initialize array of individuals
        self.__individuals = np.empty(0, dtype="object")
        self.newIndividuals(amount_of_individuals)

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.sc = self.ax.scatter(self.__position[0],self.__position[1], marker=".")
        plt.xlim(0,self._fs)
        plt.ylim(0,self._fs)
        plt.draw()
        plt.pause(self._pause)

        

    def __updatePosDir(self):
         ## array of x and y values same order as individuals
        self.__position = np.empty([2,len(self.__individuals)])
        self.__position[0,:] = np.array([ind.x for ind in self.__individuals])
        self.__position[1,:] = np.array([ind.y for ind in self.__individuals])

        ## array of dir_x and dir_y values same order as individuals
        self.__direction = np.empty([2,len(self.__individuals)])
        self.__direction[0,:] = np.array([ind.dir_x for ind in self.__individuals])
        self.__direction[1,:] = np.array([ind.dir_y for ind in self.__individuals])

    def newIndividuals(self, amount_of_individuals=1):
        x_lex = [self.Individual(self) for i in range(amount_of_individuals)]
        self.__individuals = np.sort(np.append(self.__individuals, np.array(x_lex, dtype="object")))
        self.__updatePosDir()

    def update(self):
        if self._radius_co == self._fs:
            self.mean_pos_x = np.mean(self.__position[0])
            self.mean_pos_y = np.mean(self.__position[1])
        for i in range(0, len(self.__individuals)):
            self.__individuals[i].calculateNewDirection(i)
        for ind in self.__individuals:
            ind.update()
        self.__updatePosDir()


    def getIndivByIndex(self, index):
        assert self.inRange(index), "index not in range"
        return self.__individuals[int(index)]
    
    def mapIndex(self, index):
        return index % self.__amount_of_individuals

    def distanceByIndex(self, ind1, ind2):
        #assert self.inRange(ind1) and self.inRange(ind2), "index not in range"
        ind1 = self.mapIndex(ind1)
        ind2 = self.mapIndex(ind1)

        dist_x = abs(self.__individuals[ind1].x-self.__individuals[ind2].x)
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        dist_y = abs(self.__individuals[ind1].y-self.__individuals[ind2].y)
        if (dist_y>self._fs/2):
            dist_y = self._fs-dist_y
        return dist_x+dist_y
                
    
    def xDistByIndex(self, ind1, ind2):
        ind2 = self.mapIndex(ind1)
        ind2 = self.mapIndex(ind1)
        dist_x = abs(self.__individuals[ind1].x-self.__individuals[ind2].x)
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        return dist_x

    # def distanceByIndex(self, ind1, ind2):
    #     assert self.inRange(ind1) and self.inRange(ind2), "index not in range"
    #     return abs(self.__individuals[ind1].x-self.__individuals[ind2].x)+abs(
    #         self.__individuals[ind1].y-self.__individuals[ind2].y)

    # def xDistByIndex(self, ind1, ind2):
    #     assert self.inRange(ind1) and self.inRange(ind2), "index not in range"
    #     return abs(self.__individuals[ind1].x-self.__individuals[ind2].x)

    def inRange(self, index):
        try: 
            i = int(index)
            return (i < len(self.__individuals) and i >= 0)
        except:
            return all(x in range(0,len(self.__individuals)) for x in index)

    def meanDirByIndex(self, index_list):
        assert self.inRange(index_list), "index not in range"
        x_ret = np.mean(np.array(self.__direction[0,index_list]))
        y_ret = np.mean(np.array(self.__direction[1,index_list]))
        return [x_ret, y_ret]
    
    def meanPosByIndex(self, index_list):
        assert self.inRange(index_list), "index not in range"
        x_ret = np.mean(np.array(self.__position[0,index_list]))
        y_ret = np.mean(np.array(self.__position[1,index_list]))
        return [x_ret, y_ret]

    def plot(self):
        self.sc.set_offsets(np.c_[self.__position[0],self.__position[1]])
        self.fig.canvas.draw_idle()
        if self._pause >0: plt.pause(self._pause)

    class Individual:
        def __init__(self, swarm):
            self.s = swarm
            ## define position
            self.x = float(np.random.random()*self.s._fs)
            self.y = float(np.random.random()*self.s._fs)

            ## define current direction
            self.dir_x = float(np.random.uniform(-1,1,1))
            self.dir_y = float(np.random.uniform(-1,1,1))

        def calculateNewDirection(self, index):
            sep_env = [] # small
            ali_env = [] # medium
            co_env = []  # large
            i = index

            ## find individuals in environment
            ## inc = -1: go to the left in s.individuals list
            for inc in [-1,1]:
                while self.s.inRange(i) and self.s.xDistByIndex(index, i) <= self.s._radius_sep:
                    if self.s.distanceByIndex(index, i) <= self.s._radius_sep:
                        sep_env.append(i)
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_ali:
                        ali_env.append(i)
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_co:
                        ali_env.append(i)
                    i+=inc
                ali_env += sep_env # concat
                while self.s.inRange(i) and self.s.xDistByIndex(index, i) <= self.s._radius_ali:
                    if self.s.distanceByIndex(index, i) <= self.s._radius_ali:
                        ali_env.append(i)
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_co:
                        co_env.append(i)
                    i+=inc
                if self.s._radius_co < self.s._fs: 
                    co_env += ali_env
                    while self.s.inRange(i) and self.s.xDistByIndex(index, i) <= self.s._radius_co:
                        if self.s.distanceByIndex(index, i) <= self.s._radius_ali:
                            co_env.append(i)
                        i+=inc

            ## calculate new direction, don't change order of ifs
            self.__new_dir_x = self.dir_x
            self.__new_dir_y = self.dir_y
            if len(sep_env) > 0:
                tmp = self.s.meanDirByIndex(sep_env)
                self.__new_dir_x = tmp[0]
                self.__new_dir_y = tmp[1]
            if self.s._radius_co == self.s._fs:
                self.__new_dir_x += (self.s.mean_pos_x-self.x)*self.s._weight_co
                self.__new_dir_y += (self.s.mean_pos_y-self.y)*self.s._weight_co
            elif len(co_env) > 0:
                tmp = self.s.meanPosByIndex(co_env)
                self.__new_dir_x += (tmp[0]-self.x)*self.s._weight_co
                self.__new_dir_y += (tmp[1]-self.y)*self.s._weight_co
            if len(ali_env) > 0:
                #print(ali_env)
                tmp = self.s.meanDirByIndex(ali_env)
                self.__new_dir_x += self.s._weight_ali*tmp[0]
                self.__new_dir_y += self.s._weight_ali*tmp[1]
            norm = abs(self.__new_dir_x)+abs(self.__new_dir_y)
            if norm!= 0:
                self.__new_dir_x = self.__new_dir_x/norm
                self.__new_dir_y = self.__new_dir_y/norm


        def update(self):
            self.dir_x = self.__new_dir_x
            self.dir_y = self.__new_dir_y
            #print(self.dir_x, self.dir_y)

            self.x = (self.x+self.__new_dir_x*self.s._vel) % self.s._fs
            self.y = (self.y+self.__new_dir_y*self.s._vel) % self.s._fs
            # self.x = max([min([self.x+self.__new_dir_x*self.s._vel, self.s._fs]), 0])
            # self.y = max([min([self.y+self.__new_dir_y*self.s._vel, self.s._fs]), 0])

            # if self.x == 0 or self.x==self.s._fs:
            #     self.dir_x = 0-self.dir_x
            # if self.y ==0 or self.y==self.s._fs:
            #     self.dir_y = 0-self.dir_y



        def __eq__(self, other):
            return eq(self.x, other.x)
        def __ne__(self, other):
            return ne(self.x, other.x)
        def __lt__(self, other):
            return self.x < other.x
        def __le__(self, other):
            return self.x <= other.x
        def __gt__(self, other):
            return self.x > other.x
        def __ge__(self, other):
            return self.x >= other.x

AMOUNT = 100
MAX_TIME = 10000

## create swarm
swarm = Swarm(amount_of_individuals=AMOUNT)
swarm.plot()

for t in range(0, MAX_TIME):
    swarm.update()
    swarm.plot()



input("press enter to end program")





