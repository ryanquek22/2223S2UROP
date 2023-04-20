import pandas as pd
import numpy as np
from scipy.stats import expon

from functions import * 
from constants import *

def main_b(in_initial_orders, in_rem_orders_dict, in_np_seed):
    #np.random.seed(in_np_seed)
    #Initial variables
    current_proba_dist = INITIAL_PROBA_DIST
    driver_next_free_time = DRIVER_START_TIME_MINS
    total_cost = 0
    is_dynamic = False # for dynamic pricing boolean checker

    order_tracker = {} #dict {string:int} {location: num_of_orders}
    main_order_arr = [] #arr[Order]

    # 1. Getting orders before the day has started
    # Generate an array of probabilities between 0 and 1 of length = NUM_INTIAL_ORDERS
    # For each value in the probability array, map the probability to a location based on the lower & upper bound of the probability density function
    # Keep track of total number of orders at each location with order tracker
    # Manage total orders in main_order_arr
    dummy_initial_orders = in_initial_orders
    
    #for order in np.random.uniform(0,1,size=NUM_INITIAL_ORDERS):
    for order in dummy_initial_orders:
        
        for key, val in INITIAL_PROBA_DIST.items():
            
            location = REVERSE_DISTRICT_LEGEND[key]
            if val[0] <= order <= val[1]:
                temp_order = Order(location, COST_SERVICE_UNIT)
                main_order_arr.append(temp_order)
                if location in order_tracker:
                    order_tracker[location] += 1
                else:
                    order_tracker[location] = 1
                break
    #print("Order tracker before loop is:", order_tracker)

    # 2. While loop which models the simulation based on minutes passed
    # Time period start from DRIVER_START_TIME_MINS and ends at DRIVER_END_TIME_MINS
    orders_left = NUM_OF_ORDERS_PER_DAY - NUM_INITIAL_ORDERS
    time = DRIVER_START_TIME_MINS
    rem_orders_dict = in_rem_orders_dict

    while (time < DRIVER_END_TIME_MINS):
        #print("Times is: ",time)
        
        # 3. Modeling the arrival of the reamining orders throughout the day, based on NUM_OF_ORDERS_PER_DAY
        # Each order are independent of each other and they have a certain probability of arriving by time x in the day
        # Determine if the order has arrived by current time by checking against a critera
        # if probability <= criteria, order has arrived and we check for the location and add to orders 
        # if is_dyanmic is true, DYN_COST_SERVICE_UNIT is used instead of COST_SERVICE_UNIT
        #remaining_orders = np.random.uniform(0,1, size = orders_left)
        remaining_orders = rem_orders_dict[orders_left]
        for rem_order in remaining_orders:
            criteria = expon.cdf(x= time - DRIVER_START_TIME_MINS, scale = (ORDER_CUTOFF_TIME - DRIVER_START_TIME_MINS)/(NUM_OF_ORDERS_PER_DAY-NUM_INITIAL_ORDERS))
            #print("Reamining order proba: ", rem_order)
            #print("Criteria:" ,criteria)
            if rem_order <= criteria:
                orders_left -= 1
                order_prob = np.random.uniform(0,1)
                #print("Probability of order", order_prob)
                for key, val in current_proba_dist.items():
                    rem_order_location = REVERSE_DISTRICT_LEGEND[key]
                    if val[0] <= order <= val[1]:
                        if (is_dynamic):
                            #print("Is dynamic is True")
                            temp_order = Order(rem_order_location, DYN_COST_SERVICE_UNIT)
                            main_order_arr.append(temp_order)
                        else:
                            temp_order = Order(rem_order_location, COST_SERVICE_UNIT)
                            main_order_arr.append(temp_order)
                        
                        if rem_order_location in order_tracker:
                            order_tracker[rem_order_location] += 1
                        else:
                            order_tracker[rem_order_location] = 1
                        break
        
        # 4. Clustering orders for efficiency
        # Cluster is defined to have a cluster radius <= 1, furthest distance between each location should not be more than 1 units apart
        # clusters_tracker - dict {String: Cluster}, {location: Cluster}
        #print("Start 4")
        #print(order_tracker)
        clusters_tracker = get_clusters(order_tracker, main_order_arr, SHORTEST_PATH_DICT, DISTRICT_LEGEND) 
        #print("Size of cluster tracker is",len(clusters_tracker))
        #for cluster in clusters_tracker.values():
            #print("locations in cluster is", cluster.locations)
        
        # 5. Driver serves a cluster
        # Driver has to come back to the start location before being able to serve
        # Sort & Serve the cluster with the highest number of orders first
        # Use a greedy algorithm to do vehicle routing
        # update main_order_arr, order_tracker, clusters_tracker
        if (driver_next_free_time <= time and len(clusters_tracker) > 0):
            #print("Serving a cluster")
            cluster_arr = [] # arr of tuples representing (Location, Cluster)
            for str_name, cluster in clusters_tracker.items():
                cluster_arr.append((str_name, cluster))
            
            cluster_arr = sorted(cluster_arr, key = lambda x: x[1].num_of_orders, reverse=True) 
            cluster_to_serve = cluster_arr[0][1]
            #print("Driver serving cluster of", cluster_to_serve.locations)
            
            time_to_add_to_driver = get_driver_next_free_time(START_LOCATION, cluster_to_serve, SHORTEST_PATH_DICT, DISTRICT_LEGEND, TIME_TRAVELLING_UNIT, TIME_SERVICE_UNIT)
            
            if (driver_next_free_time + time_to_add_to_driver <= DRIVER_END_TIME_MINS):
                driver_next_free_time += time_to_add_to_driver
                total_cost += cluster_to_serve.get_cluster_cost(START_LOCATION, SHORTEST_PATH_DICT, DISTRICT_LEGEND, COST_TRAVELLING_UNIT)
            
                main_order_arr = remove_orders_from_main_arr(main_order_arr, cluster_to_serve.orders)
                order_tracker = remove_orders(order_tracker, cluster_to_serve.locations)
                clusters_tracker.pop(cluster_arr[0][0])
        
        # 6. Determining if there is a remote cluster that can be served via (a) dynamic pricing (b) or outsourcing
        # A remote cluster is defined to be a cluster with num_of_orders to be < 2
        # It is possible to have multiple remote clusters
        temp_arr_cluster = [] #arr[Cluster]
        for clust in clusters_tracker.values(): 
            if (clust.num_of_orders) < 2:
                temp_arr_cluster.append(clust)

        '''
        ## Alternative strategy a - Dynamic Pricing
        ## Adjust current_proba_dist to reflect dynamic pricing for ALL remote clusters
        ## Swing value of 0.2 to represent increase in coverage in these locations 
        ## With more coverage, the new orders incoming are more likely to go these locations 
        current_proba_dist = get_new_proba_dist(INITIAL_PROBA_DIST, START_LOCATION, temp_arr_cluster, SHORTEST_PATH_DICT, REVERSE_DISTRICT_LEGEND) # potential to add swing value here
        is_dynamic = check_proba_dist_similairity(current_proba_dist, INITIAL_PROBA_DIST)
        print(is_dynamic)
        print("Currrent Proba dist is: ",current_proba_dist)
        ## END OF Alternative strategy a
        '''
        
        
        ## Alternative strategy b - Outsourcing
        ## Collate all orders that can be outsourced from the remote clusters
        ## Probability of third party accepting the delivery is modeled after the current_offering_price against theoretical_maximum_price 
        ## Current offering price is a function of time
        ## Theoretical maximum offering price is inclusive of Traveling costs and Penalty costs
        ## If generated probability is <= acceptance probability, order is successfully outsourced
        ## add current_offering_price to total cost and remove order from cluster, order_tracker, main_order_arr
        orders_that_can_be_outsourced = get_outsourcing_orders(temp_arr_cluster) # arr of orders    
        for os_order in orders_that_can_be_outsourced:
            theoretical_maximum_offering_price = get_theoretical_maximum_offering_price(os_order, START_LOCATION, SHORTEST_PATH_DICT, DISTRICT_LEGEND, PENALTY_UNIT, TIME_TRAVELLING_UNIT)
            current_offering_price = get_current_offering_price(os_order, START_LOCATION, SHORTEST_PATH_DICT, DISTRICT_LEGEND, PENALTY_UNIT, TIME_TRAVELLING_UNIT, time, DRIVER_START_TIME_MINS, DRIVER_END_TIME_MINS)
            #current_acceptance_proability = max(current_offering_price / theoretical_maximum_offering_price, 0.7)
            current_acceptance_proability = current_offering_price / theoretical_maximum_offering_price
            probability_of_successfully_outsourcing = np.random.uniform(0,1)
            if probability_of_successfully_outsourcing <= current_acceptance_proability:
                #print("Successful outsource of order at location", os_order.location)
                
                total_cost += current_offering_price
                if order_tracker[os_order.location] == 1:      
                    order_tracker.pop(os_order.location)
                else:    
                    curr_num = order_tracker[os_order.location]
                    order_tracker[os_order.location] = curr_num - 1
                #print(main_order_arr)
                main_order_arr.remove(os_order) 
        
        #print("Driver Next Free Time", driver_next_free_time)    
        #print("Current cost is", total_cost)
        #print("Remaning orders",order_tracker)
        #print('#'*50)
        time +=30

    # 7. After Driver has ended work
    # Apply penalty for unfulfilled_orders    
    for unfulfilled_orders in order_tracker.values():
        total_cost += unfulfilled_orders * PENALTY_UNIT   
        
    #print(total_cost)
    return total_cost

