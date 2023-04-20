import pandas as pd
from scipy.stats import expon
import numpy as np
from classes import *
import random as rnd

from simulation import *
from simulation_a import *
from simulation_b import *

main_arr = []
main_a_arr = []
main_b_arr = []

iter = 100000

for i in range(1,iter+1):
    INITIAL_ORDERS = np.random.uniform(0,1,size=NUM_INITIAL_ORDERS)

    REM_ORDERS_DICT = {
        0:[],
        1:np.random.uniform(0,1,size=1),
        2:np.random.uniform(0,1,size=2),
        3:np.random.uniform(0,1,size=3),
        4:np.random.uniform(0,1,size=4),
        5:np.random.uniform(0,1,size=5),
        6:np.random.uniform(0,1,size=6),
        7:np.random.uniform(0,1,size=7),
        8:np.random.uniform(0,1,size=8),
        9:np.random.uniform(0,1,size=9),
        10:np.random.uniform(0,1,size=10),
        11:np.random.uniform(0,1,size=11),
        12:np.random.uniform(0,1,size=12),
        13:np.random.uniform(0,1,size=13),
        14:np.random.uniform(0,1,size=14),
        15:np.random.uniform(0,1,size=15),
        16:np.random.uniform(0,1,size=16),
        17:np.random.uniform(0,1,size=17),
        18:np.random.uniform(0,1,size=18),
        19:np.random.uniform(0,1,size=19),
        20:np.random.uniform(0,1,size=20),
    }
    main_arr.append(main(INITIAL_ORDERS, REM_ORDERS_DICT, i))

for j in range(1,iter + 1):
    #np.random.seed(i)
    INITIAL_ORDERS = np.random.uniform(0,1,size=NUM_INITIAL_ORDERS)

    REM_ORDERS_DICT = {
        0:[],
        1:np.random.uniform(0,1,size=1),
        2:np.random.uniform(0,1,size=2),
        3:np.random.uniform(0,1,size=3),
        4:np.random.uniform(0,1,size=4),
        5:np.random.uniform(0,1,size=5),
        6:np.random.uniform(0,1,size=6),
        7:np.random.uniform(0,1,size=7),
        8:np.random.uniform(0,1,size=8),
        9:np.random.uniform(0,1,size=9),
        10:np.random.uniform(0,1,size=10),
        11:np.random.uniform(0,1,size=11),
        12:np.random.uniform(0,1,size=12),
        13:np.random.uniform(0,1,size=13),
        14:np.random.uniform(0,1,size=14),
        15:np.random.uniform(0,1,size=15),
        16:np.random.uniform(0,1,size=16),
        17:np.random.uniform(0,1,size=17),
        18:np.random.uniform(0,1,size=18),
        19:np.random.uniform(0,1,size=19),
        20:np.random.uniform(0,1,size=20),
    }
    main_a_arr.append(main_a(INITIAL_ORDERS, REM_ORDERS_DICT, j))

for k in range(1,iter + 1):
    #np.random.seed(i)
    INITIAL_ORDERS = np.random.uniform(0,1,size=NUM_INITIAL_ORDERS)

    REM_ORDERS_DICT = {
        0:[],
        1:np.random.uniform(0,1,size=1),
        2:np.random.uniform(0,1,size=2),
        3:np.random.uniform(0,1,size=3),
        4:np.random.uniform(0,1,size=4),
        5:np.random.uniform(0,1,size=5),
        6:np.random.uniform(0,1,size=6),
        7:np.random.uniform(0,1,size=7),
        8:np.random.uniform(0,1,size=8),
        9:np.random.uniform(0,1,size=9),
        10:np.random.uniform(0,1,size=10),
        11:np.random.uniform(0,1,size=11),
        12:np.random.uniform(0,1,size=12),
        13:np.random.uniform(0,1,size=13),
        14:np.random.uniform(0,1,size=14),
        15:np.random.uniform(0,1,size=15),
        16:np.random.uniform(0,1,size=16),
        17:np.random.uniform(0,1,size=17),
        18:np.random.uniform(0,1,size=18),
        19:np.random.uniform(0,1,size=19),
        20:np.random.uniform(0,1,size=20),
    }
    main_b_arr.append(main_b(INITIAL_ORDERS, REM_ORDERS_DICT, k))

df = pd.DataFrame({"main" : main_arr,
                   "main_a_arr" : main_a_arr,
                   "main_b_arr" : main_b_arr
})

df.to_csv('results_100000.csv')
