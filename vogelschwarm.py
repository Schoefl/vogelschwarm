## idee: klasse Schwarmmitglied oder so, die globale Variablen ernthaelt und klasse bird erbt?
# bzw ein schwarm ist eine Klasse, in der alle birds abgespeichert werden, schwarm bekommt als Parameter 
# ob bird oder fish

import numpy as np
from matplotlib import pyplot as plt
import sys
import time 
from KeyPoller import KeyPoller

## in python 2, classes work differently (must inherite object in our case)
if sys.version_info[0] < 3:
    raise Exception("Python 3 is required, you are using ",
     sys.version_info[0])


class Swarm:
    ## ToDo: improve seperation method
    def __init__(self, amount_of_individuals=50):
        self.__amount_of_individuals = 0
        ## changeable parameters
        self._fs = 1                       # field size [0,_fs]x[0,_fs]
        self._vel = 0.01*self._fs          # velocity 
        self._radius_sep = 0.03*self._fs   # radius for seperation
        self._radius_ali = 0.3*self._fs    # radius for alignment
        self._radius_co  = self._fs        # radius for cohesion 0.5
        self._weight_ali = 1               # weight for alignment
        self._weight_co  = 1.5             # weight for cohesion
        self._weight_sep = 10              # weight for seperation
        self._pause = 0.0001               # pause between steps must not be 0

        ## initialize array of individuals
        self.__individuals = np.empty(0, dtype="object")
        self.newIndividuals(amount_of_individuals)

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.sc = self.ax.scatter(self.__position[0,:],self.__position[1,:], marker=".")
        plt.xlim(0,self._fs)
        plt.ylim(0,self._fs)
        # plt.draw()
        # plt.pause(self._pause)

    def changeParameters(self):
        print("""If you have finished changing parameters press [q] + [ENTER]
        Current Parameters:
        [1] field size: {}
        [2] velocity: {}
        [3] seperation radius (as factor of field size): {}*field_size
        [4] alignment radius (as factor of field size): {}*field_size
        [5] cohesion radius (as factor of field size): {}*field_size
        [6] seperation weight: {}
        [7] alignment weight: {}
        [8] cohesion weight: {}
        [9] pause between steps"""
        .format(self._fs, self._vel, self._radius_sep/self._fs, self._radius_ali/self._fs, 
        self._radius_co/self._fs, self._weight_sep, self._weight_ali, self._weight_co, self._pause))

        while True:
            no = input("type number of parameter you want to change + [ENTER] or [q] + [ENTER] to escape \n")
            if no == "q": break
            if no == "1":
                value = input("type value + [ENTER] \n")
                try: 
                    if int(value)>0:
                        self._fs = int(value)
                        plt.xlim(0,self._fs)
                        plt.ylim(0,self._fs)
                    else:
                        print("value should be positive integer")
                except:
                    print("value should be positive integer")
            elif no == "2":
                value = input("type value + [ENTER] \n")
                try: 
                    if float(value)>0:
                        self._vel = float(value)
                    else:
                        print("value should be positive float")
                except:
                    print("value should be positive float")
            elif no == "3":
                value = input("type value + [ENTER] \n")
                try: 
                    if float(value)>0 and float(value)<=1 and float(value)<=self._radius_ali:
                        self._radius_sep = float(value)*self._fs
                    else:
                        print("value should be positive float that is smaller than 1 and smaller than alignment radius")
                except:
                    print("value should be positive float that is smaller than 1 and smaller than alignment radius")
            elif no == "4":
                value = input("type value + [ENTER] \n")
                try: 
                    if float(value)>0 and float(value)<=1 and float(value)<=self._radius_co and float(value)>=self._radius_sep:
                        self._radius_ali = float(value)*self._fs
                    else:
                        print("value should be positive float that is smaller than 1 and between seperation and cohesion radius")
                except:
                    print("value should be positive float that is smaller than 1 and between seperation and cohesion radius")
            elif no == "5":
                value = input("type value + [ENTER] \n")
                try: 
                    if float(value)>0 and float(value)<=1 and float(value)>=self._radius_ali:
                        self._radius_co = float(value)*self._fs
                    else:
                        print("value should be positive float that is smaller than 1 and geater than seperation radius")
                except:
                    print("value should be positive float that is smaller than 1 and greater than seperation radius")
            elif no == "6":
                value = input("type value + [ENTER] \n")
                try:
                    self._weight_sep = float(value)
                except:
                    print("value should be float")
            elif no == "7":
                value = input("type value + [ENTER] \n")
                try:
                    self._weight_ali = float(value)
                except:
                    print("value should be float")
            elif no == "8":
                value = input("type value + [ENTER] \n")
                try:
                    self._weight_co = float(value)
                except:
                    print("value should be float")
            elif no == "9":
                value = input("type value + [ENTER] \n")
                try:
                    if float(value) > 0: self._pause = float(value)
                except:
                    print("value should be positive float")
            else:
                print("invalid input")

        

    def __updatePosDir(self):
         ## array of x and y values same order as individuals
        self.__position = np.empty([2,self.__amount_of_individuals])
        self.__position[0,:] = np.array([ind.x for ind in self.__individuals])
        self.__position[1,:] = np.array([ind.y for ind in self.__individuals])

        ## array of dir_x and dir_y values same order as individuals
        self.__direction = np.empty([2,len(self.__individuals)])
        self.__direction[0,:] = np.array([ind.dir_x for ind in self.__individuals])
        self.__direction[1,:] = np.array([ind.dir_y for ind in self.__individuals])

    def newIndividuals(self, amount_of_individuals=1):
        assert int(amount_of_individuals)>0, "must be positive integer"
        x_lex = [self.Individual(self) for i in range(int(amount_of_individuals))]
        self.__amount_of_individuals += int(amount_of_individuals)
        self.__individuals = np.sort(np.append(self.__individuals, np.array(x_lex, dtype="object")))
        self.__updatePosDir()
    
    def delIndividuals(self, amount_of_individuals=1):
        assert int(amount_of_individuals)>0, "must be positive integer"
        amount_of_individuals = int(amount_of_individuals)
        if amount_of_individuals >= self.__amount_of_individuals:
            print("delete all birds except one instead of {}".format(amount_of_individuals))
            amount_of_individuals = self.__amount_of_individuals-1
        remaining = np.random.randint(self.__amount_of_individuals, size=self.__amount_of_individuals-amount_of_individuals)
        ## ToDo: make sure destructor gets called (?)
        self.__individuals = np.sort(self.__individuals[remaining])
        self.__amount_of_individuals -= amount_of_individuals
        

    def update(self):
        if self._radius_co == self._fs:
            self.mean_pos_x = np.mean(self.__position[0,:])
            self.mean_pos_y = np.mean(self.__position[1,:])
        for i in range(0, len(self.__individuals)):
            self.__individuals[i].calculateNewDirection(i)
        for ind in self.__individuals:
            ind.update()
        self.__updatePosDir()
        self.__individuals = np.sort(self.__individuals)
    
    def mapIndex(self, index):
        return index % self.__amount_of_individuals

    def distanceByIndex(self, ind1, ind2):
        ind1 = self.mapIndex(ind1)
        ind2 = self.mapIndex(ind2)

        dist_x = abs(self.__individuals[ind1].x-self.__individuals[ind2].x)
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        dist_y = abs(self.__individuals[ind1].y-self.__individuals[ind2].y)
        if (dist_y>self._fs/2):
            dist_y = self._fs-dist_y
        return dist_x+dist_y
                
    
    def xDistByIndex(self, ind1, ind2):
        ind1 = self.mapIndex(ind1)
        ind2 = self.mapIndex(ind2)
        dist_x = abs(self.__individuals[ind1].x-self.__individuals[ind2].x)
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        return dist_x

    def inRange(self, index):
        try: 
            i = int(index)
            return (i < len(self.__individuals) and i >= 0)
        except:
            return all(x in range(0,len(self.__individuals)) for x in index)

    def meanDirByIndex(self, index_list):
        if type(index_list) == set:
            index_list = list(index_list)

        assert self.inRange(index_list), "index not in range"
        x_ret = np.mean(np.array(self.__direction[0,index_list]))
        y_ret = np.mean(np.array(self.__direction[1,index_list]))
        return np.array([x_ret, y_ret])
    
    def meanPosByIndex(self, index_list):
        if type(index_list) == set:
            index_list = list(index_list)
        assert self.inRange(index_list), "index not in range"
        x_ret = np.mean(np.array(self.__position[0,index_list]))
        y_ret = np.mean(np.array(self.__position[1,index_list]))
        return np.array([x_ret, y_ret])

    def plot(self):
        self.sc.set_offsets(np.c_[self.__position[0,:],self.__position[1,:]])
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
            # print("calculateNewDirection")
            sep_env = set() # small
            ali_env = set([index]) # medium
            co_env = set([index])  # large
            i = index
            # print(sep_env)
            ## find individuals in environment
            ## inc = -1: go to the left in s.individuals list
            for inc in [-1,1]:
                i = index+inc
                while self.s.mapIndex(i) != index and self.s.xDistByIndex(index, i) <= self.s._radius_sep:
                    if self.s.distanceByIndex(index, i) <= self.s._radius_sep:
                        sep_env.add(self.s.mapIndex(i))
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_ali:
                        ali_env.add(self.s.mapIndex(i))
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_co:
                        co_env.add(self.s.mapIndex(i))
                    i+=inc
                ali_env = ali_env.union(sep_env)
                while self.s.mapIndex(i) != index and self.s.xDistByIndex(index, i) <= self.s._radius_ali:
                    if self.s.distanceByIndex(index, i) <= self.s._radius_ali:
                        ali_env.add(self.s.mapIndex(i))
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_co:
                        co_env.add(self.s.mapIndex(i))
                    i+=inc
                if self.s._radius_co < self.s._fs: 
                    co_env = co_env.union(ali_env)
                    while self.s.mapIndex(i) != index and self.s.xDistByIndex(index, i) <= self.s._radius_co:
                        if self.s.distanceByIndex(index, i) <= self.s._radius_ali:
                            co_env.add(self.s.mapIndex(i))
                        i+=inc

            ## calculate new direction, don't change order of ifs
            self.__new_dir_x = self.dir_x
            self.__new_dir_y = self.dir_y
            if len(sep_env) > 0:
                #print("sep_env: {}".format(sep_env))
                tmp = self.s.meanDirByIndex(sep_env)
                old = np.array([self.dir_x, self.dir_y])
                self.__new_dir_x = tmp[0]*self.s._weight_sep
                self.__new_dir_y = tmp[1]*self.s._weight_sep


                if abs(np.dot(tmp, old)/np.sqrt((old*old).sum())/np.sqrt((tmp*tmp).sum())) > 0.8:
                    #print("way to close")
                    weight = self.s._weight_sep
                    tmp2 = self.s.meanPosByIndex(sep_env)
                    #mult = np.random.randint(-1,1)
                    if (index % 2) == 0:
                        mult = -1
                    else:
                        mult = 1
                    if self.y-tmp2[1] == 0:
                        #print("random y dir")
                        self.__new_dir_y = self.dir_y + mult*self.s._radius_sep*weight
                    else:
                        self.__new_dir_y = self.dir_y+(self.y-tmp2[1])/(abs(self.y-tmp2[1]))*self.s._radius_sep*weight
                    if self.x-tmp2[0] == 0:
                        #print("random x dir")
                        self.__new_dir_x = self.dir_x + mult*self.s._radius_sep*weight
                    else:
                        self.__new_dir_x = self.dir_x+(self.x-tmp2[0])/(abs(self.x-tmp2[0]))*self.s._radius_sep*weight

                    # self.__new_dir_y = self.dir_y+(self.y-tmp2[1])/(abs(self.y-tmp2[1]))*self.s._radius_sep/2
                    # self.__new_dir_x = self.dir_x+(self.x-tmp2[0])/(abs(self.x-tmp2[0]))*self.s._radius_sep/2


                # tmp1 = self.s.meanPosByIndex(sep_env)

                # if abs(self.x - tmp1[0]) < abs(self.y - tmp1[1]):
                #     self.__new_dir_x = 0-self.dir_x
                #     self.__new_dir_y = tmp[1]
                # else:
                #     self.__new_dir_y = 0-self.dir_y
                #     self.__new_dir_x = tmp[0]

                
                #     self.__new_dir_x = 0-self.dir_x
                #     self.__new_dir_y = tmp[1]
                # else:
                #     self.__new_dir_x = tmp[0]
                #     self.__new_dir_y = 0-self.dir_y
            if self.s._radius_co == self.s._fs:
                self.__new_dir_x += (self.s.mean_pos_x-self.x)*self.s._weight_co
                self.__new_dir_y += (self.s.mean_pos_y-self.y)*self.s._weight_co
            elif len(co_env) > 0:
                tmp = self.s.meanPosByIndex(co_env)
                self.__new_dir_x += (tmp[0]-self.x)*self.s._weight_co
                self.__new_dir_y += (tmp[1]-self.y)*self.s._weight_co
            if len(ali_env) > 0:
                # print(ali_env)
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

amount = input("How many individuls should the swarm contain? input [amount of individuals] + [ENTER] \n")

## create swarm
swarm = Swarm(amount_of_individuals=int(amount))
with KeyPoller() as keyPoller:
    print("""if you want to end the program press [q]
    if you want to change the swarm parameters press [p] 
    if you want to add individuals press [a] 
    if you want to delete individuals press [d]""")
    
    while True:
        tmp = keyPoller.poll()
        if not tmp is None:
            if tmp == "q":
                break
            elif tmp== "p":
                swarm.changeParameters()
            elif tmp == "a":
                value = input("input [amount to add] + [ENTER]\n")
                try: 
                    if int(value)>0: 
                        swarm.newIndividuals(int(value))
                    else: 
                        print("input should be positive integer")
                except:
                    print("input should be positive integer")
            elif tmp=="d":
                value = input("input [amount to delete] + [ENTER]\n")
                try: 
                    if int(value)>0: 
                        swarm.delIndividuals(int(value))
                    else: 
                        print("input should be positive integer")
                except:
                    print("input should be positive integer")
            else:
                print("invalid input")
                
        swarm.update()
        swarm.plot()







