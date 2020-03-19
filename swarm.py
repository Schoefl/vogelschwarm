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

    def __updatePosDir(self):
        """
        update position and direction array for all individuals
        self.__individuals should be sorted before calling this function
        """
         ## array of x and y values are in the same order as self.__individuals
        self.__position = np.empty([2,self.__amount_of_individuals])
        self.__position[0,:] = np.array([ind.pos[0] for ind in self.__individuals])
        self.__position[1,:] = np.array([ind.pos[1] for ind in self.__individuals])

        ## direction array is in in the same order as self.__individuals
        self.__direction = np.empty([2,self.__amount_of_individuals])
        self.__direction[0,:] = np.array([ind.dir[0] for ind in self.__individuals])
        self.__direction[1,:] = np.array([ind.dir[1] for ind in self.__individuals])



    def newIndividuals(self, amount_of_individuals=1):
        """
        function: create amount_of_individuals new individuals and add them to self.__individuals list
        input:    amount_of_individuals, integer, default 1
        output:   none
        """
        assert int(amount_of_individuals)>0, "must be positive integer"
        x_lex = [self.Individual(self) for i in range(int(amount_of_individuals))]
        self.__amount_of_individuals += int(amount_of_individuals)
        self.__individuals = np.sort(np.append(self.__individuals, np.array(x_lex, dtype="object")))
        self.__updatePosDir()
        print(amount_of_individuals, " new individuals created")

    
    def delIndividuals(self, amount_of_individuals=1):
        """
        function: delete amount_of_individuals individuals from self.__individuals list
        input:    amount_of_individuals, integer, default 1
        output:   none
        """
        assert int(amount_of_individuals)>0, "must be positive integer"
        amount_of_individuals = int(amount_of_individuals)
        if amount_of_individuals >= self.__amount_of_individuals:
            print("delete all birds except one instead of {}".format(amount_of_individuals))
            amount_of_individuals = self.__amount_of_individuals-1
        to_del = np.random.choice(self.__amount_of_individuals, size=amount_of_individuals, replace=False)
        # ToDo: make sure destructor is called (?)
        rem = np.delete(self.__individuals, to_del)
        self.__individuals = np.sort(rem)
        self.__amount_of_individuals -= amount_of_individuals
        self.__updatePosDir()  
        print(amount_of_individuals, " individuals deleted")

    def update(self):
        """
        function: update position and direction of individuals
        input:    none
        output:   none
        """
        if self._radius_co == self._fs:
            self.mean_pos = np.mean(self.__position, axis=1)
        for i in range(0, self.__amount_of_individuals):
            self.__individuals[i].calculateNewDirection(i)
        for ind in self.__individuals:
            ind.update()
        self.__updatePosDir()
        self.__individuals = np.sort(self.__individuals)
    
    def mapIndex(self, index):
        """
        input:    positive integer
        output:   index in range(0,self.__amount_of_individuals) 
        """
        return int(index) % self.__amount_of_individuals

    def distanceByIndex(self, ind1, ind2):
        """
        function: compute distance (manhattan metric) between two individuals
        input:    index of individuals in sorted list self.__individuals
        output:   flaot, distance
        """
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
        """
        function: test if index is in range of (0, self.__amount_of_individuals)
        input:    list or set of indices of individuals in sorted array self.__individuals
        output:   bool, True if in range, False if not
        """
        ind1 = self.mapIndex(ind1)
        ind2 = self.mapIndex(ind2)
        dist_x = abs(self.__individuals[ind1].pos[0]-self.__individuals[ind2].pos[0])
        if (dist_x>self._fs/2):
            dist_x = self._fs-dist_x
        return dist_x

    def angleByIndex(self, ind_self, ind_other):
        """
        function: test if bird "other" is in sight range of bird "self"
        input:    indices of individuals in sorted array self.__individuals
        output:   bool, True if in range, False if not
        """
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
        """
        function: test if index is in range of (0, self.__amount_of_individuals)
        input:    list or set of indices of individuals in sorted array self.__individuals
        output:   bool, True if in range, False if not
        """
        try: 
            i = int(index)
            return (i < self.__amount_of_individuals and i >= 0)
        except:
            return all(x in range(0,self.__amount_of_individuals) for x in index)

    def meanDirByIndex(self, index_list):
        """
        function: calculate average direction of a individuals given by index_list
        input:    list or set of indices of individuals in sorted array self.__individuals
        output:   two dimensional array containing average direction where ret_val[0]..x, ret_val[1]..y
        """
        if type(index_list) == set:
            index_list = list(index_list)

        assert self.inRange(index_list), "index not in range"
        ret_val = np.mean(np.array(self.__direction[:,index_list]), axis=1)
        return ret_val
    
    def meanPosByIndex(self, index_list):
        """
        function: calculate center of mass of a individuals given by index_list
        input:    list or set of indices of individuals in sorted array self.__individuals
        output:   two dimensional array containing center of mass where ret_val[0]..x, ret_val[1]..y
        """
        if type(index_list) == set:
            index_list = list(index_list)
        assert self.inRange(index_list), "index not in range"
        ret_val = np.mean(np.array(self.__position[:,index_list]), axis=1)
        return ret_val
    
    def getIndivByIndex(self, index):
        """
        function: get func
        input:    index of individual in sorted array self.__individuals
        output:   none
        """
        assert self.inRange(index), "index not in range"
        return self.__individuals[int(index)]

    def plot(self):
        """
        function: plot swarm in scatter plot (each individual is a dot)
        input:    none
        output:   none
        """
        self.__sc.set_offsets(np.c_[self.__position[0,:],self.__position[1,:]])
        self.__fig.canvas.draw_idle()
        if self._pause >0: plt.pause(self._pause)
    
    def changeParameters(self):
        """
        function: change changeable parameters via comand line inputs
        input:    none
        output:   none
        """
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

    class Individual:
        """ 
        nested class containing individuals (agents) and their properties
        """
        def __init__(self, swarm):
            self.s = swarm
            ## define position pos[0]..x, pos[1]..y
            self.pos = np.array([float(np.random.random()*self.s._fs), float(np.random.random()*self.s._fs)])
            ## define current direction
            self.dir = np.array([float(np.random.uniform(-1,1,1)), float(np.random.uniform(-1,1,1))])

        ## overload functions to compare objects
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
        
        def update(self):
            """
            function: update direction and position of individual
            input:    none
            output:   none
            """
            self.dir = self.__new_dir
            self.pos[0] = (self.pos+self.__new_dir*self.s._vel)[0] % self.s._fs
            self.pos[1] = (self.pos+self.__new_dir*self.s._vel)[1] % self.s._fs

        def calculateNewDirection(self, index):
            """
            function: calculate new direction for this individual and store it in self.__new_dir
            input:    index of this individual in sorted array swarm.__individual
            return:   none
            """

            sep_env = set() # small
            ali_env = set([index]) # medium
            co_env = set([index])  # large
            i = index
            
            ## find individuals in environment
            ## inc = -1: go to the left in s.individuals list, inc = 1: go to the right
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

            ## calculate seperation vector
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
      
            ## calculate cohision vector
            if self.s._radius_co == self.s._fs:
                ## if cohision radius is field size don't calculate mean every time
                self.__new_dir += (self.s.mean_pos-self.pos)*self.s._weight_co
            elif len(co_env) > 0:
                ## if cohision radius smaller than field size and birds in cohision radius
                ## calculate mean position
                tmp = self.s.meanPosByIndex(co_env)
                self.__new_dir += (tmp-self.pos)*self.s._weight_co
            if len(ali_env) > 0:
                ## if birds in alignment radius calculate mean direction
                tmp = self.s.meanDirByIndex(ali_env)
                self.__new_dir += tmp*self.s._weight_ali
            ## norm new direction vector
            norm = np.linalg.norm(self.__new_dir)
            if norm!= 0:
                self.__new_dir = self.__new_dir/norm


amount = input("How many individuals should the swarm contain? input [amount of individuals] + [ENTER] \n")

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







