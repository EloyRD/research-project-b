from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

import random
import numpy as np

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from .rpb_agents import FoodPatch, SleepPatch, Animal

class SleepAnimals(Model):
    '''
    Analysis of the evolution of sleep in animals
    '''

    # Default values
    width               = 40
    height              = 40
    
    number_food_patch   = 40
    number_sleep_patch  = 40

    interdistance_factor    = 0.7
    intradistance_factor    = 0.2

    fp_depletion_tick   = 60
        
    def __init__(self, model_id , genome,width = 40, height = 40, 
                 number_food_patch = 40, number_sleep_patch = 40,
                 interdistance_factor = 0.7, intradistance_factor = 0.2,
                 fp_depletion = 60, sleep_and_food_gainfactor = 1):
        super().__init__()
        
        # Setting Parameters
        self.model_id               = model_id
        self.width                  = width
        self.height                 = height
        self.number_food_patch      = number_food_patch
        self.number_sleep_patch     = number_sleep_patch
        self.interdistance_factor   = interdistance_factor
        self.intradistance_factor   = intradistance_factor
        self.sue_factor             = sleep_and_food_gainfactor

        self.genome = genome

        self.fp_center_x = 0
        self.fp_center_y = 0
        self.sp_center_x = 0
        self.sp_center_y = 0

        self.current_id_food_patch  = 0
        self.current_id_sleep_patch = 0

        self.fp_tick_to_depletion   = fp_depletion

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus = False)
        self.datacollector = DataCollector(
           agent_reporters={"Food_fitness"  : lambda a: a.fitness_food,
                            "Sleep_fitness" : lambda a: a.fitness_sleep,
                            "Fitness"       : lambda a: a.fitness,
                            "Mode"          : lambda a: a.mode,
                            "Direction"     : lambda a: a.lookingto})
        
        # Picking Centers for Food and Sleep Patches
        self.interdistance = 0
        self.intradistance = 0
        self.findingcenters()

        # Populating Food Patches
        self.available_food_patches = self.grid.get_neighborhood( (self.fp_center_x, self.fp_center_y), False, True, self.intradistance )
        i = 0
        while i < self.number_food_patch:
            self.new_foodpatch()
            i += 1

        # Populating Sleep Patches
        self.available_sleep_patches = self.grid.get_neighborhood( (self.sp_center_x, self.sp_center_y), False, True, self.intradistance )
        i = 0
        while i < self.number_sleep_patch:
            current_spot = random.choice(self.available_sleep_patches)
            if not self.grid.is_cell_empty(current_spot):
                continue
            sleep_patch = SleepPatch( self.next_id_sleeppatch(), self, current_spot )
            self.grid.place_agent( sleep_patch, current_spot )
            i += 1
        
        # Adding Animal to the world
        current_spot = random.choice( self.grid.empties )
        animal = Animal( self.next_id(), self, current_spot, self.genome, self.sue_factor, self.sue_factor )
        self.grid.place_agent( animal, current_spot )
        self.schedule.add( animal )
        

    def step(self):
        '''Advance the model by one step.'''
        self.datacollector.collect(self)
        self.schedule.step()

    def findingcenters(self):
        max_manhattan_length = self.height + self.width
        self.interdistance = int(max_manhattan_length * self.interdistance_factor)
        self.intradistance = int(max_manhattan_length * self.intradistance_factor)

        fp_center_x = 0
        fp_center_y = 0
        sp_center_x = 0
        sp_center_y = 0
        
        centers_selected = False

        while not centers_selected:
            fp_center_x = random.randrange(self.width)
            fp_center_y = random.randrange(self.height)
            fp_center = (fp_center_x, fp_center_y)
            
            available_spots_food = self.grid.get_neighborhood(fp_center, False, False, self.intradistance)
            if len(available_spots_food) < 80:
                continue
            
            if self.interdistance > 0:
                list_centers_sp = list( set( self.grid.get_neighborhood(fp_center, False, False, self.interdistance + 1) ) - 
                                        set( self.grid.get_neighborhood(fp_center, False, False, self.interdistance - 1) ) )
                if len(list_centers_sp) < 5:
                    continue
            else:
                list_centers_sp = [(fp_center_x,fp_center_y)]

            sp_center = random.choice(list_centers_sp)
            (sp_center_x, sp_center_y) = sp_center

            available_spots_sleep = self.grid.get_neighborhood(sp_center, False, False, self.intradistance)
            if len(available_spots_sleep) < 80:
                continue

            centers_selected = True

        self.fp_center_x = fp_center_x
        self.fp_center_y = fp_center_y
        self.sp_center_x = sp_center_x
        self.sp_center_y = sp_center_y

    def next_id_foodpatch(self):
        """ Return the next unique ID for food patches, increment current_id"""
        self.current_id_food_patch += 1
        a = 'M' + str(self.model_id) + 'F' + str(self.current_id_food_patch)
        return a

    def next_id_sleeppatch(self):
        """ Return the next unique ID for sleep patches, increment current_id"""
        self.current_id_sleep_patch += 1
        a = 'M' + str(self.model_id) + 'S' + str(self.current_id_sleep_patch)
        return a

    def new_foodpatch(self):
        spot_found = False
        while not spot_found :
            current_spot = random.choice(self.available_food_patches)
            if not self.grid.is_cell_empty(current_spot):
                continue
            food_patch = FoodPatch(self.next_id_foodpatch(), self, current_spot, self.fp_tick_to_depletion)
            self.grid.place_agent(food_patch, current_spot)
            spot_found = True

    def arrayRGB_clusters(self):
        available_spots = np.full( (self.grid.width , self.grid.height , 3) , 255)
        for coordinates in self.available_sleep_patches:
            (x, y) = coordinates
            available_spots[x][y]= [100, 0, 150]
        for coordinates in self.available_food_patches:
            (x, y) = coordinates
            available_spots[x][y]= [10, 150, 0]
        return available_spots

    def arrayRGB_display(self):
        RGBdisplay = np.full((self.grid.width, self.grid.height,3), 255)
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = list(cell_content)
            if len(a) == 0:
                RGBdisplay[x][y] = [255,255,255]
            elif len(a) == 1:
                if      isinstance(a[0], SleepPatch):
                    RGBdisplay[x][y] = [100,0,150]
                elif    isinstance(a[0], FoodPatch):
                    RGBdisplay[x][y] = [10,150,0]
                elif    isinstance(a[0], Animal):
                    RGBdisplay[x][y] = [0,0,0]
                else:
                    pass
            elif len(a) == 2:
                RGBdisplay[x][y] = [0,0,0]
            else:
                pass
        return RGBdisplay

    def array2D_display(self):
        display2D = np.zeros((self.grid.width, self.grid.height))
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = list(cell_content)
            if len(a) == 0:
                display2D[x][y] = 0
            elif len(a) == 1:
                if isinstance(a[0], SleepPatch):
                    display2D[x][y] = 10
                elif isinstance(a[0], FoodPatch):
                    display2D[x][y] = 20
                elif isinstance(a[0], Animal):
                    display2D[x][y] = 30
                else:
                    pass
            else:
                pass
        return display2D

class SleepAnimals_sinDataColl(Model):
    '''
    Analysis of the evolution of sleep in animals
    '''

    # Default values
    width               = 40
    height              = 40
    
    number_food_patch   = 40
    number_sleep_patch  = 40

    interdistance_factor    = 0.7
    intradistance_factor    = 0.2

    fp_depletion_tick   = 60
        
    def __init__(self, model_id , genome,width = 40, height = 40, 
                 number_food_patch = 40, number_sleep_patch = 40,
                 interdistance_factor = 0.7, intradistance_factor = 0.2,
                 fp_depletion = 60, sleep_and_food_gainfactor = 1):
        super().__init__()
        
        # Setting Parameters
        self.model_id               = model_id
        self.width                  = width
        self.height                 = height
        self.number_food_patch      = number_food_patch
        self.number_sleep_patch     = number_sleep_patch
        self.interdistance_factor   = interdistance_factor
        self.intradistance_factor   = intradistance_factor
        self.sue_factor             = sleep_and_food_gainfactor
        self.genome = genome

        self.fp_center_x = 0
        self.fp_center_y = 0
        self.sp_center_x = 0
        self.sp_center_y = 0

        self.current_id_food_patch  = 0
        self.current_id_sleep_patch = 0

        self.fp_tick_to_depletion   = fp_depletion

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus = False)
        #self.datacollector = DataCollector(
        #   agent_reporters={"Food_fitness"  : lambda a: a.fitness_food,
        #                    "Sleep_fitness" : lambda a: a.fitness_sleep,
        #                    "Fitness"       : lambda a: a.fitness,
        #                    "Mode"          : lambda a: a.mode,
        #                    "Direction"     : lambda a: a.lookingto})
        
        # Picking Centers for Food and Sleep Patches
        self.interdistance = 0
        self.intradistance = 0
        self.findingcenters()

        # Populating Food Patches
        self.available_food_patches = self.grid.get_neighborhood( (self.fp_center_x, self.fp_center_y), False, True, self.intradistance )
        i = 0
        while i < self.number_food_patch:
            self.new_foodpatch()
            i += 1

        # Populating Sleep Patches
        self.available_sleep_patches = self.grid.get_neighborhood( (self.sp_center_x, self.sp_center_y), False, True, self.intradistance )
        i = 0
        while i < self.number_sleep_patch:
            current_spot = random.choice(self.available_sleep_patches)
            if not self.grid.is_cell_empty(current_spot):
                continue
            sleep_patch = SleepPatch( self.next_id_sleeppatch(), self, current_spot )
            self.grid.place_agent( sleep_patch, current_spot )
            i += 1
        
        # Adding Animal to the world
        current_spot = random.choice( self.grid.empties )
        animal = Animal( self.next_id(), self, current_spot, self.genome, self.sue_factor, self.sue_factor )
        self.grid.place_agent( animal, current_spot )
        self.schedule.add( animal )
        

    def step(self):
        '''Advance the model by one step.'''
#        self.datacollector.collect(self)
        self.schedule.step()

    def findingcenters(self):
        max_manhattan_length = self.height + self.width
        self.interdistance = int(max_manhattan_length * self.interdistance_factor)
        self.intradistance = int(max_manhattan_length * self.intradistance_factor)

        fp_center_x = 0
        fp_center_y = 0
        sp_center_x = 0
        sp_center_y = 0
        
        centers_selected = False

        while not centers_selected:
            fp_center_x = random.randrange(self.width)
            fp_center_y = random.randrange(self.height)
            fp_center = (fp_center_x, fp_center_y)
            
            available_spots_food = self.grid.get_neighborhood(fp_center, False, False, self.intradistance)
            if len(available_spots_food) < 80:
                continue
            
            if self.interdistance > 0:
                list_centers_sp = list( set( self.grid.get_neighborhood(fp_center, False, False, self.interdistance + 1) ) - 
                                        set( self.grid.get_neighborhood(fp_center, False, False, self.interdistance - 1) ) )
                if len(list_centers_sp) < 5:
                    continue
            else:
                list_centers_sp = [(fp_center_x,fp_center_y)]

            sp_center = random.choice(list_centers_sp)
            (sp_center_x, sp_center_y) = sp_center

            available_spots_sleep = self.grid.get_neighborhood(sp_center, False, False, self.intradistance)
            if len(available_spots_sleep) < 80:
                continue

            centers_selected = True

        self.fp_center_x = fp_center_x
        self.fp_center_y = fp_center_y
        self.sp_center_x = sp_center_x
        self.sp_center_y = sp_center_y

    def next_id_foodpatch(self):
        """ Return the next unique ID for food patches, increment current_id"""
        self.current_id_food_patch += 1
        a = 'M' + str(self.model_id) + 'F' + str(self.current_id_food_patch)
        return a

    def next_id_sleeppatch(self):
        """ Return the next unique ID for sleep patches, increment current_id"""
        self.current_id_sleep_patch += 1
        a = 'M' + str(self.model_id) + 'S' + str(self.current_id_sleep_patch)
        return a

    def new_foodpatch(self):
        spot_found = False
        while not spot_found :
            current_spot = random.choice(self.available_food_patches)
            if not self.grid.is_cell_empty(current_spot):
                continue
            food_patch = FoodPatch(self.next_id_foodpatch(), self, current_spot, self.fp_tick_to_depletion)
            self.grid.place_agent(food_patch, current_spot)
            spot_found = True

    def arrayRGB_clusters(self):
        available_spots = np.full( (self.grid.width , self.grid.height , 3) , 255)
        for coordinates in self.available_sleep_patches:
            (x, y) = coordinates
            available_spots[x][y]= [100, 0, 150]
        for coordinates in self.available_food_patches:
            (x, y) = coordinates
            available_spots[x][y]= [10, 150, 0]
        return available_spots

    def arrayRGB_display(self):
        RGBdisplay = np.full((self.grid.width, self.grid.height,3), 255)
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = list(cell_content)
            if len(a) == 0:
                RGBdisplay[x][y] = [255,255,255]
            elif len(a) == 1:
                if      isinstance(a[0], SleepPatch):
                    RGBdisplay[x][y] = [100,0,150]
                elif    isinstance(a[0], FoodPatch):
                    RGBdisplay[x][y] = [10,150,0]
                elif    isinstance(a[0], Animal):
                    RGBdisplay[x][y] = [0,0,0]
                else:
                    pass
            elif len(a) == 2:
                RGBdisplay[x][y] = [0,0,0]
            else:
                pass
        return RGBdisplay

    def array2D_display(self):
        display2D = np.zeros((self.grid.width, self.grid.height))
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = list(cell_content)
            if len(a) == 0:
                display2D[x][y] = 0
            elif len(a) == 1:
                if isinstance(a[0], SleepPatch):
                    display2D[x][y] = 10
                elif isinstance(a[0], FoodPatch):
                    display2D[x][y] = 20
                elif isinstance(a[0], Animal):
                    display2D[x][y] = 30
                else:
                    pass
            else:
                pass
        return display2D