import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random

from agents import Animal, FoodPatch, SleepPatch
from model import SleepAnimals

a = np.random.choice(['feeding' , 'sleeping' , 'flexible'] , 24)
model1 = SleepAnimals(1, a)