import numpy as np

from functions import *

START_LOCATION = "PAYA LEBAR" #4 on legend

DRIVER_START_TIME_MINS = 600 #10am
DRIVER_END_TIME_MINS = 1140 #7pm
ORDER_CUTOFF_TIME = 960 #4pm

NUM_OF_DISCRETE_WAVES = 3 #tbc
NUM_OF_ORDERS_PER_DAY = 30
NUM_INITIAL_ORDERS = 18

COST_TRAVELLING_UNIT = 7.5/9 # Based on disel price of 2.50 per L
COST_SERVICE_UNIT = 110/540 # based on salary of $3300 per month 
DYN_COST_SERVICE_UNIT = 110/540 * 1.2 # larger than normal cost_service_unit as we will lose profit/ increase cost as the customer pays less money


TIME_TRAVELLING_UNIT = 5
TIME_SERVICE_UNIT = 7
PENALTY_UNIT = 100 #100 dollars

INITIAL_PROBA_DIST = get_initial_proba_dist()
DISTRICT_LEGEND, REVERSE_DISTRICT_LEGEND, SHORTEST_PATH_DICT = create_shortest_path_dict()

