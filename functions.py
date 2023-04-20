import pandas as pd
from scipy.stats import poisson
import math

from classes import *

# Create shortest path dict, district_legend, reverse_district_legend
def create_shortest_path_dict():
    shortest_path_df = pd.read_csv('final_matrix.csv', index_col=0)
    districts = pd.read_csv('districts.csv')
    
    legend = {} # dict {int:String} {location_index : location}
    reverse_legend = {} # dict {String : int} {location : location_index}
    output = {} # dict {String: arr[int]} {location : shortest_dist_arr}
    count = 0
    for i in range (0,40):
        legend[districts.iloc[i][0]] = count
        reverse_legend[count] = districts.iloc[i][0]
        temp = []
        for val in shortest_path_df.iloc[i]:
            temp.append(val)
        output[districts.iloc[i][0]] = temp
        count += 1
    return legend, reverse_legend, output

# Create a dictionary that contains the probability cdf for each location
def get_initial_proba_dist():
    proba = pd.read_csv('initial_proba.csv', index_col=0) 
    output = {} # dict {int: [int, int]} {location_index: [lower, upper]}
    for i in range(0,40):
        temp = []
        temp.append(proba.iloc[i,0])
        temp.append(proba.iloc[i,1])
        output[i] = temp
    
    return output    

# Get total number of orders for cluster and breakdown of location and number of orders from locations identified
def get_num_of_orders(arr, current_orders):
    arr_order_output = [] #array of tuples arr[String, int] arr[location, num_of_orders]
    output = 0
    for loc in arr:
        output += current_orders[loc]
        arr_order_output.append((loc, current_orders[loc]))
    return output, arr_order_output

# Get an array of orders from main_order_arr that belong to the same location as that in location_arr
def get_order_array(location_arr, main_order_arr): 
    order_arr = [] #arr[Order]
    for loc in location_arr:
        for order in main_order_arr:
            if loc == order.location:
                order_arr.append(order)
    return order_arr

# Check if location is within the radius of 1 from current location
def check_location_in_cluster_radius(curr_location, temp_list, distance_dict, district_legend):
    for loc in temp_list:
        if distance_dict[curr_location][district_legend[loc]] > 2:
            return False
    return True

# Creating clusters based on current orders
def get_clusters(current_orders, main_order_arr, distance_matrix, district_legend):
    # dict {String: int} {location : num_of_orders}
    #print("Get CLusters method")
    #print("Current orders",current_orders)
    #print("Main order arr", main_order_arr)
    if (len(current_orders)==0):
        return {}
    
    
    temp = {} # dict {string, arr[string]} {initial string : array of locations inside this cluster}
    key_list = [] # arr[String] array of initial locations
    val_list = [] # arr[int] array of num_of_orders at each location
    for key, val in current_orders.items():
        key_list.append(key)
        val_list.append(val)
    '''
    Possible optimisation of combining into a single arr and sort based on num of orders before forming clusters
    '''
    
    locations_processed = [] # arr[String] array of locations that we have processed from current orders
    for i in range (0, len(key_list)):
        temp_list = [key_list[i]]
        for j in range(i+1, len(key_list)):
            # Avoid having duplicates in locations across clusters
            if key_list[j] in locations_processed or key_list[i] in locations_processed:
                continue
            
            if check_location_in_cluster_radius(key_list[j], temp_list, distance_matrix, district_legend):
                temp_list.append(key_list[j])
                temp[key_list[i]] = temp_list
                locations_processed.append(key_list[j])
        locations_processed.append(key_list[i])
        #print("Locations processed",locations_processed)
    #print("temp", temp)
    
    # edge case when there is only 1 location, still create a cluster for that location
    #if (len(key_list) == 1): 
    if (len(temp) == 0):
        temp[key_list[0]] = temp_list
    
    output = {} # dict {string, cluster}, {initial string : Cluster}
    for location, location_arr in temp.items():
        num_of_orders, dummy = get_num_of_orders(location_arr, current_orders)
        arr_orders = get_order_array(location_arr, main_order_arr)
        temp_cluster = Cluster(locations=location_arr, num_of_orders=num_of_orders, order_arr=arr_orders)
        output[location_arr[0]] = temp_cluster
    return output
        
# removing orders from order_tracker
def remove_orders(current_order_tracker, cluster_locations):
    for location in cluster_locations:
        current_order_tracker.pop(location)
    return current_order_tracker

# removing orders from main_arr
def remove_orders_from_main_arr(main_order_arr, cluster_orders):
    for order in cluster_orders:
        main_order_arr.remove(order)
    return main_order_arr

# Calculate time taken to serve cluster with greedy algorithm
def get_driver_next_free_time(START_LOCATION, cluster_to_serve, SHORTEST_PATH_DICT, DISTRICT_LEGEND, TIME_TRAVELLING_UNIT, TIME_SERVICE_UNIT):
    # Greedy Algorithm for vehicle routing
    # Travel to nearest location from current location
    output = 0
    orders_arr = cluster_to_serve.orders
    start = START_LOCATION
    
    while len(orders_arr) > 0:
        # Select location to travel to based on shortest travel distance from current location
        orders_arr = sorted(orders_arr, key = lambda x: SHORTEST_PATH_DICT[start][DISTRICT_LEGEND[x.location]]) 
        order = orders_arr[0]
        orders_arr.pop(0)
        
        #print("Start is: ",start)
        #print("destinations is ", order[0])
        
        # for orders that are in the same location, it is unrealistic to assume that they take no time at all
        # every order will require traveling time and service time
        output += (SHORTEST_PATH_DICT[start][DISTRICT_LEGEND[order.location]]+1 * TIME_TRAVELLING_UNIT + TIME_SERVICE_UNIT)
        start = order.location
    
    # Account for the timet taken to cover the distance between start_location and last location
    #print("Final place before returning to start is: ", start)
    output += SHORTEST_PATH_DICT[start][DISTRICT_LEGEND[START_LOCATION]]+1 * TIME_TRAVELLING_UNIT
    return output


# Adjust new probability distribution based on swing value    
def get_new_proba_dist(INITIAL_PROBA_DIST, START_LOCATION, arr_cluster, SHORTEST_PATH_DICT, REVERSE_DISTRICT_LEGEND):
    
    locations_to_adjust = [] #arr[String] array of locations to increaes the probability for
    for cluster in arr_cluster:
        for locations in cluster.locations:
            locations_to_adjust.append(locations)
    
    if (len(locations_to_adjust) == 0):
        return INITIAL_PROBA_DIST
    #print("length of loactions to adjust", len(locations_to_adjust))
    
    total_adjustment_swing = 0.2 #can be modified
    
    # uniform increase and decrase based on previous values of probability distribution
    positive_bias = total_adjustment_swing/len(locations_to_adjust)
    negative_bias = -total_adjustment_swing/ (len(INITIAL_PROBA_DIST) - len(locations_to_adjust))
    start = 0
    
    output_proba_dist = {} #dict {int, arr[int, int]} {location_index : [lower, upper]}
    for key, val in INITIAL_PROBA_DIST.items():
        temp = []
        prev_val = val[1] - val[0]
        if REVERSE_DISTRICT_LEGEND[key] in locations_to_adjust:
            temp.append(start)
            temp.append(start+(prev_val +positive_bias))
            output_proba_dist[key] = temp
            #print("temp value being added is", temp)
            start += (prev_val + positive_bias)
            
        else:
            temp.append(start)
            temp.append(start+(prev_val + negative_bias))
            output_proba_dist[key] = temp
            start += (prev_val + negative_bias)
        
        assert(round(start, 5) <= 1), "start should be  < 1"
    return output_proba_dist
    
# Checking if there is a change is probability distribution to enable is_dynamic and DYN_COST_SERVICE_UNIT
def check_proba_dist_similairity(current_proba_dist, INITIAL_PROBA_DIST):
    for i in range(len(INITIAL_PROBA_DIST)):
        if current_proba_dist[i] != INITIAL_PROBA_DIST[i]:
            return True #True because is_dynamic is now True
    return False #False because is_dyanmic is now false

# Create an array of orders           
def get_outsourcing_orders(temp_cluster_arr):
    output_orders = [] # arr[Order] array of Orders
    for clus in temp_cluster_arr:
        for order in clus.orders:
            output_orders.append(order)
    return output_orders

# calculate theoretical maximum offering price
def get_theoretical_maximum_offering_price(order, START_LOCATION, shortest_dist_dict, district_legend, PENALTY_UNIT, time_travelling_unit):
    output = PENALTY_UNIT + shortest_dist_dict[START_LOCATION][district_legend[order.location]] * time_travelling_unit
    return output

# calculate current offering price based on total cost taken to travel + exponetial ratio of the penatly unit
def get_current_offering_price(order, START_LOCATION, SHORTEST_DIST_DICT, district_legend, PENALTY_UNIT, TIME_TRAVELLING_UNIT, current_time, DRIVER_START_TIME, DRIVER_END_TIME):
    #order shortest_dist * time_traveling_unit + exp^(current time/time left) * penalty) / exp
    output = TIME_TRAVELLING_UNIT * SHORTEST_DIST_DICT[START_LOCATION][district_legend[order.location]] + PENALTY_UNIT*(math.e**((current_time - DRIVER_START_TIME)/ (DRIVER_END_TIME - DRIVER_START_TIME)))/math.e
    return output
    

    
