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
    ## ToDo: fix bugs with param input and delete function
    def __init__(self, amount_of_individuals=50):
        self.__amount_of_individuals = 0
        ## changeable parameters
        self._fs = 1                       # field size [0,_fs]x[0,_fs]
        self._vel = 0.02*self._fs          # velocity 
        self._radius_sep = 0.01*self._fs   # radius for seperation
        self._radius_ali = 0.2*self._fs    # radius for alignment
        self._radius_co  = self._fs        # radius for cohesion
        self._weight_ali = 3               # weight for alignment
        self._weight_co  = 1               # weight for cohesion
        self._weight_sep = 3               # weight for seperation
        self._pause = 0.00001              # pause between steps must not be 0
        self._cos_angle = -0.5             # cos(sight_angle)

        ## initialize array of individuals
        self.__individuals = np.empty(0, dtype="object")
        self.newIndividuals(amount_of_individuals)

        plt.ion()
        self.__fig, self.__ax = plt.subplots()
        self.__sc = self.__ax.scatter(self.__position[0,:],self.__position[1,:], marker=".")
        plt.xlim(0,self._fs)
        plt.ylim(0,self._fs)


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
        [9] pause between steps: {}
        [10] cos of range of vision: {}"""
        .format(self._fs, self._vel, self._radius_sep/self._fs, self._radius_ali/self._fs, 
        self._radius_co/self._fs, self._weight_sep, self._weight_ali, self._weight_co, self._pause, self._cos_angle))

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
                    if float(value) > 0: 
                        self._pause = float(value)
                    else:
                        print("value should be positive float")
                except:
                    print("value should be positive float")
            elif no == "10":
                value = input("type value + [ENTER] \n")
                try:
                    if float(value) > -1 and float(value) < 1: 
                        self._pause = float(value)
                    else:
                        print("value should be float between -1 and 1")
                except:
                    print("value should be float between -1 and 1")
            else:
                print("invalid input")

        

    def __updatePosDir(self):
         ## array of x and y values same order as individuals
        self.__position = np.empty([2,self.__amount_of_individuals])
        self.__position[0,:] = np.array([ind.pos[0] for ind in self.__individuals])
        self.__position[1,:] = np.array([ind.pos[1] for ind in self.__individuals])

        ## direction array in same order as individuals
        self.__direction = np.empty([2,self.__amount_of_individuals])
        self.__direction[0,:] = np.array([ind.dir[0] for ind in self.__individuals])
        self.__direction[1,:] = np.array([ind.dir[1] for ind in self.__individuals])

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
        to_del = np.random.randint(self.__amount_of_individuals, size=amount_of_individuals)
        ## ToDo: make sure destructor gets called (?)
        rem = np.delete(self.__individuals, to_del)
        self.__individuals = np.sort(rem)
        self.__amount_of_individuals -= amount_of_individuals
        self.__updatePosDir()

        

    def update(self):
        if self._radius_co == self._fs:
            self.mean_pos = np.mean(self.__position, axis=1)
        for i in range(0, self.__amount_of_individuals):
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

        dist_x = abs(self.__individuals[ind1].pos[0]-self.__individuals[ind2].pos[0])
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        dist_y = abs(self.__individuals[ind1].pos[1]-self.__individuals[ind2].pos[1])
        if (dist_y>self._fs/2):
            dist_y = self._fs-dist_y
        return dist_x+dist_y
                
    
    def xDistByIndex(self, ind1, ind2):
        ind1 = self.mapIndex(ind1)
        ind2 = self.mapIndex(ind2)
        dist_x = abs(self.__individuals[ind1].pos[0]-self.__individuals[ind2].pos[0])
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        return dist_x

    def angleByIndex(self, ind_self, ind_other):
        ret_val = False
        ind_self = self.mapIndex(ind_self)
        ind_other = self.mapIndex(ind_other)
        a = self.getIndivByIndex(ind_self).dir
        b = self.getIndivByIndex(ind_other).pos-self.getIndivByIndex(ind_self).pos
        try: 
            ret_val = np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)) > self._cos_angle
        except:
            ## case if one of the vecor norms is zero
            ret_val = True
        return ret_val

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
        ret = np.mean(np.array(self.__direction[:,index_list]), axis=1)
        return ret
    
    def meanPosByIndex(self, index_list):
        if type(index_list) == set:
            index_list = list(index_list)
        assert self.inRange(index_list), "index not in range"
        ret = np.mean(np.array(self.__position[:,index_list]), axis=1)
        return ret
    
    def getIndivByIndex(self, index):
        assert self.inRange(index), "index not in range"
        return self.__individuals[int(index)]

    def plot(self):
        self.__sc.set_offsets(np.c_[self.__position[0,:],self.__position[1,:]])
        self.__fig.canvas.draw_idle()
        if self._pause >0: plt.pause(self._pause)

    class Individual:
        def __init__(self, swarm):
            self.s = swarm
            ## define position pos[0]..x, pos[1]..y
            self.pos = np.array([float(np.random.random()*self.s._fs), float(np.random.random()*self.s._fs)])

            ## define current direction
            self.dir = np.array([float(np.random.uniform(-1,1,1)), float(np.random.uniform(-1,1,1))])

        def calculateNewDirection(self, index):
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
                    if self.s.distanceByIndex(index, i) <= self.s._radius_ali and self.s.angleByIndex(index,i):
                        ali_env.add(self.s.mapIndex(i))
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_co and self.s.angleByIndex(index,i):
                        co_env.add(self.s.mapIndex(i))
                    i+=inc
                while self.s.mapIndex(i) != index and self.s.xDistByIndex(index, i) <= self.s._radius_ali:
                    if self.s.distanceByIndex(index, i) <= self.s._radius_ali and self.s.angleByIndex(index,i):
                        ali_env.add(self.s.mapIndex(i))
                    elif self.s.distanceByIndex(index, i) <= self.s._radius_co and self.s.angleByIndex(index,i):
                        co_env.add(self.s.mapIndex(i))
                    i+=inc
                if self.s._radius_co < self.s._fs: 
                    co_env = co_env.union(ali_env)
                    while self.s.mapIndex(i) != index and self.s.xDistByIndex(index, i) <= self.s._radius_co:
                        if self.s.distanceByIndex(index, i) <= self.s._radius_co  and self.s.angleByIndex(index,i):
                            co_env.add(self.s.mapIndex(i))
                        i+=inc

            ## calculate new direction, don't change order of ifs
            self.__new_dir = self.dir

            ## calculate seperation
            if len(sep_env) > 0:
                new_dir = np.array([0,0], dtype=float)

                for i in sep_env:
                    tmp = self.pos-np.array([self.s.getIndivByIndex(i).pos[0], self.s.getIndivByIndex(i).pos[1]])
                    weight = self.s.distanceByIndex(index, i)
                    if weight == 0: weight = 1/self.s._radius_sep
                    try:
                        new_dir += tmp/float((abs(tmp[0])+abs(tmp[1])))/weight
                    except:
                        print("would divide by zero in calculateNewDirection")
                        # ToDo: think about what to do if (abs(tmp[0])+abs(tmp[1])) == 0, though very unlikely

                new_dir = new_dir/len(sep_env)
                self.__new_dir += new_dir*self.s._weight_sep


                
                # #if abs(np.dot(tmp, old)/np.sqrt((old*old).sum())/np.sqrt((tmp*tmp).sum())) > 0.8:

            
        
            if self.s._radius_co == self.s._fs:
                self.__new_dir += (self.s.mean_pos-self.pos)*self.s._weight_co
            elif len(co_env) > 0:
                tmp = self.s.meanPosByIndex(co_env)
                self.__new_dir += (tmp-self.pos)*self.s._weight_co
            if len(ali_env) > 0:
                # print(ali_env)
                tmp = self.s.meanDirByIndex(ali_env)
                self.__new_dir += tmp*self.s._weight_ali
            norm = np.linalg.norm(self.__new_dir)
            if norm!= 0:
                self.__new_dir = self.__new_dir/norm
            


        def update(self):
            self.dir = self.__new_dir
            self.pos[0] = (self.pos+self.__new_dir*self.s._vel)[0] % self.s._fs
            self.pos[1] = (self.pos+self.__new_dir*self.s._vel)[1] % self.s._fs

        def __eq__(self, other):
            return eq(self.pos[0], other.pos[0])
        def __ne__(self, other):
            return ne(self.pos[0], other.pos[0])
        def __lt__(self, other):
            return self.pos[0] < other.pos[0]
        def __le__(self, other):
            return self.pos[0] <= other.pos[0]
        def __gt__(self, other):
            return self.pos[0] > other.pos[0]
        def __ge__(self, other):
            return self.pos[0] >= other.pos[0]

amount = input("How many individuls should the swarm contain? input [amount of individuals] + [ENTER] \n")

## create swarm
swarm = Swarm(amount_of_individuals=int(amount))
with KeyPoller() as keyPoller:
    print("""if you want to end the program press [q]
    if you want to change the swarm parameters press [p] 
    if you want to add individuals press [a] 
    if you want to delete individuals press [d] 
    (there are still some bugs, I'll try to fix, sorry for that)""")
    
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







