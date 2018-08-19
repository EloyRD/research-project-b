from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import math

from itertools import groupby

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

def genome_alternatives(quantity):
    a = np.random.choice(['eat' , 'sleep' , 'flex'] , (quantity, 24))
    return a

def mutation_gene(a,p):
    roll = random.uniform(0,1)
    options = ['eat' , 'sleep' , 'flex']
    if roll < p:
        options.remove(a)
        return random.choice(options)
    else:
        return a

def dataframe_generation(generation_number , generation_list):
    i   = generation_number + 1
    
    tuples_row  = []
    for j in range (1, 101):
        a   = ( ordinal(i) , str(j).zfill(3) )
        tuples_row.append(a)
    index_row   = pd.MultiIndex.from_tuples(tuples_row, names=['generation', 'individual'])
    
    tuples_col  = [ ( '' , 'unique_id' ) ,  ( '' , 'fitness')]
    for i in range (1 , 25):
        b   = ('genome', i)
        tuples_col.append(b)
    index_col   = pd.MultiIndex.from_tuples(tuples_col)

    index_col = ['u_id','fitness','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24']

    struc_list  = list()

    for k in range( len(generation_list) ):
        tup = ()
        tup = tup + (generation_list[k][0],)
        tup = tup + (generation_list[k][1],)
        for l in range(24):
            a   = generation_list[k][2][l]
            a   = a[0].capitalize()
            tup = tup + (a,)
        struc_list.append(tup)

    dt  = np.dtype([('u_id', '<i4'), ('fitness', '<f8'), ('1', '<U1'), ('2', '<U1'), ('3', '<U1'), ('4', '<U1'), ('5', '<U1'), ('6', '<U1'), ('7', '<U1'), ('8', '<U1'), ('9', '<U1'), ('10', '<U1'), ('11', '<U1'), ('12', '<U1'), ('13', '<U1'), ('14', '<U1'), ('15', '<U1'), ('16', '<U1'), ('17', '<U1'), ('18', '<U1'), ('19', '<U1'), ('20', '<U1'), ('21', '<U1'), ('22', '<U1'), ('23', '<U1'), ('24', '<U1')])


    struc_array = np.array( struc_list, dtype=dt )

    df  = pd.DataFrame(struc_array , index= index_row , columns= index_col)

    return df

def displayRGB_generation(gen_id , top ,  gener_array):
    RGBdisplay = np.full( (26, top, 3), 255 )
    for i in range(top):
        for k in range(24):
            a = gener_array[gen_id - 1][i][2][k]
            if a == 'sleep':
                RGBdisplay[k+1][i]= [10, 150, 0   ]
            if a == 'eat':
                RGBdisplay[k+1][i]= [100, 0, 150 ]
            if a == 'flex':
                RGBdisplay[k+1][i]= [0, 250, 255 ]
            else:
                pass
    return RGBdisplay

def phases_in_genome(genome):
    z = list( genome )
    z = [ x[0] for x in groupby(z) ]
    z = [ z[j] for j in range ( -2,len(z) ) ]
    z = [ x[0] for x in groupby(z) ]

    y = [(z[i],z[i+1],z[i+2]) for i in range( 0,len(z)-2) ]

    a = y.count( ('eat', 'flex', 'eat') )
    b = y.count( ('sleep', 'flex', 'sleep') )
    c = y.count( ('sleep', 'flex', 'eat') ) + y.count( ('eat', 'flex', 'sleep') )

    return (a,b,c)
