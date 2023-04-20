class Cluster:
    def __init__(self, locations, num_of_orders, order_arr) -> None:
        self.locations = locations #arr[String] array of locations (allow duplicates)
        self.num_of_orders = num_of_orders # int
        self.orders = order_arr #arr[Order], each order is [location, cost service unit]
        ##cost per order as a metric?
        
    def __str__(self):
        return f"Locations in this cluster are {self.locations} with a total number of {self.num_of_orders} orders"
    
    # calculate cost required to serve cluster
    def get_cluster_cost(self, START_LOCATION, SHORTEST_PATH_DICT, DISTRICT_LEGEND, COST_TRAVELLING_UNIT):    
        # Greedy algorithm similar to caluclating time taken for driver to finish serving cluster
        output = 0
        orders_arr = self.orders
        start = START_LOCATION
        #print("Length of order_arr is ",len(orders_arr))
        while len(orders_arr) > 0:
            #print("Calculating cost")
            #print("Start location is", start)
            
            #print("length of order arr",len(orders_arr))
            orders_arr = sorted(orders_arr, key = lambda x: SHORTEST_PATH_DICT[start][DISTRICT_LEGEND[x.location]]) # Select location to travel to based on shortest travel distance from current location
            order = orders_arr[0]
            orders_arr.pop(0)
            #print("destination is ", order.location)
            #print("Start is: ",start)
            #print("destinations is ", order[0])
            # Still expecting some cost from travelig point to point
            output += (SHORTEST_PATH_DICT[start][DISTRICT_LEGEND[order.location]]+1 * COST_TRAVELLING_UNIT + order.cost_service_unit)
            #print(start)
            start = order.location

        # Account for the cost between start_location and last location
        #print("Final place before returning to start is: ", start)
        output += SHORTEST_PATH_DICT[start][DISTRICT_LEGEND[START_LOCATION]]+1 * COST_TRAVELLING_UNIT
        return output
    
    

class Order:
    def __init__(self, location, cost_service_unit):
        self.location = location #String
        self.cost_service_unit = cost_service_unit #int
    
    def __str__(self):
        return f"Order at {self.location} with a cost_service_unit {self.cost_service_unit}"
    