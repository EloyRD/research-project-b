from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

import random
import numpy as np

from mesa import Agent

class Animal(Agent):
    '''
    An animal that goes around looking for Food Patches and Sleep Patches,
    '''
    def __init__(self, unique_id, model, pos, genomearr, sleep_factor = 1, food_factor = 1):
        super().__init__(unique_id, model)
        self.pos            = pos
        self.direction      = random.randint(0,23)
        self.sleep_energy   = 0
        self.food_energy    = 0
        self.hour_of_day    = 0
        self.circadian_rythm = genomearr
        self.objective      = 'sleep'
        self.fitness_food   = .5
        self.fitness_sleep  = .5
        self.fitness        = .5
        self.mode           = 0
        self.lookingto      = None
        self.looking()
        self.minutes_asleep = 0

        self.sleep_factor   = sleep_factor
        self.food_factor    = food_factor

    def step(self):
        # Find hour of the day
        self.will_move      = True
        self.mode           = 0
        self.hour_of_day    = int ( ( self.model.schedule.time % 24 ) / 60 )
        self.define_objective()
        self.behaviour_about_objective()

        if self.will_move:
            self.sleep_energy   = self.sleep_energy - ( 1 * self.sleep_factor  )
            self.food_energy    = self.food_energy  - ( 1 * self.food_factor   )
            self.decide_direction()
            self.move()

        self.calculate_fitness()
        self.looking()
        
    def define_objective(self):
        if self.circadian_rythm[self.hour_of_day] == 'sleep' :
            self.objective      = 'sleep'
        if self.circadian_rythm[self.hour_of_day] == 'eat' :
            self.objective      = 'eat'
        if self.circadian_rythm[self.hour_of_day] == 'flex' :
            if self.fitness_sleep + .1 < self.fitness_food:
                self.objective  = 'sleep'
            elif self.fitness_food + .1 < self.fitness_sleep:
                self.objective  = 'eat'
            else:
                pass

    def behaviour_about_objective(self):
        this_cell   = self.model.grid.get_cell_list_contents([self.pos])
        food        = [obj for obj in this_cell if isinstance(obj, FoodPatch)]
        sleep       = [obj for obj in this_cell if isinstance(obj, SleepPatch)]

        a   = self.model.fp_tick_to_depletion
                
        if ( ( self.objective   == 'sleep' )   and (len(sleep) > 0) ):
            self.sleep_energy   = self.sleep_energy + 3 * self.sleep_factor
            self.mode           = -10
            self.will_move      = False
            self.minutes_asleep += 1
        elif ( ( self.objective   == 'eat' )    and (len(food) > 0) ):
            self.food_energy    = self.food_energy  + (3*  (fp_energyfactor(a) * food[0].death_ticks) ) * self.food_factor
            food[0].death_ticks -= 1
            self.will_move      = False
            self.mode           = 10
            if food[0].death_ticks < 0:
                self.model.grid._remove_agent(self.pos, food[0])
                self.model.new_foodpatch()
            else:
                pass
        else:
            pass

    def decide_direction(self):
        inrange = False
        while not inrange:
            a = random.randint(-1,1)
            self.direction  = self.direction + a
            self.direction  = self.direction % 24
            dx = 0
            dy = 0
            if ( self.direction in [23, 0, 1]):
                dx = 1
                dy = 0
            if ( self.direction in [2, 3, 4]):
                dx = 1
                dy = 1
            if ( self.direction in [5, 6, 7]):
                dx = 0
                dy = 1
            if ( self.direction in [8, 9, 10]):
                dx = -1
                dy = 1
            if ( self.direction in [11, 12, 13]):
                dx = -1
                dy = 0
            if ( self.direction in [14, 15, 16]):
                dx = -1
                dy = -1
            if ( self.direction in [17, 18, 19]):
                dx = 0
                dy = -1
            if ( self.direction in [20, 21, 22]):
                dx = 1
                dy = -1
            (x, y) = self.pos
            nx = x + dx
            ny = y + dy
            if not self.model.grid.out_of_bounds((nx,ny)):
                inrange = True
    
    def move(self):
        dx = 0
        dy = 0
        if ( self.direction in [23, 0, 1]):
            dx = 1
            dy = 0
        if ( self.direction in [2, 3, 4]):
            dx = 1
            dy = 1
        if ( self.direction in [5, 6, 7]):
            dx = 0
            dy = 1
        if ( self.direction in [8, 9, 10]):
            dx = -1
            dy = 1
        if ( self.direction in [11, 12, 13]):
            dx = -1
            dy = 0
        if ( self.direction in [14, 15, 16]):
            dx = -1
            dy = -1
        if ( self.direction in [17, 18, 19]):
            dx = 0
            dy = -1
        if ( self.direction in [20, 21, 22]):
            dx = 1
            dy = -1
        (x, y) = self.pos
        new_position = (x + dx, y + dy)
        self.model.grid.move_agent(self, new_position)

    def calculate_fitness(self):
        self.fitness_food   = 1 / ( 1 + np.exp(self.food_energy * (-1/100) ) )
        self.fitness_sleep  = 1 / ( 1 + np.exp(self.sleep_energy * (-1/100) ) )    
        self.fitness        = (self.fitness_food + self.fitness_sleep) / 2

    def looking(self):
        if ( self.direction in [23, 0, 1]):
            self.lookingto = 'RIGHT'
        if ( self.direction in [2, 3, 4]):
            self.lookingto = 'TOP-RIGHT'
        if ( self.direction in [5, 6, 7]):
            self.lookingto = 'TOP'
        if ( self.direction in [8, 9, 10]):
            self.lookingto = 'TOP-LEFT'
        if ( self.direction in [11, 12, 13]):
            self.lookingto = 'LEFT'
        if ( self.direction in [14, 15, 16]):
            self.lookingto = 'BOTTOM-LEFT'
        if ( self.direction in [17, 18, 19]):
            self.lookingto = 'BOTTOM'
        if ( self.direction in [20, 21, 22]):
            self.lookingto = 'BOTTOM-RIGHT'

class FoodPatch(Agent):
    '''
    A patch with food
    '''

    def __init__(self, unique_id, model, pos, depletion_ticks):
        '''
        Creates a new Food Patch
        '''
        super().__init__(unique_id, model)
        self.pos = pos
        self.death_ticks = depletion_ticks

    def step(self):
        pass

class SleepPatch(Agent):
    '''
    A patch to sleep
    '''
    def __init__(self, unique_id, model, pos):
        '''
        Creates a new Sleep Patch
        '''
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        pass

fp_energyfactor = lambda n: (n) / (n*(1+n)/2)