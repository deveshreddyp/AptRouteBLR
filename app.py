import heapq
import copy
import random
from collections import deque
from flask import Flask, jsonify, request
from flask_cors import CORS

# Import the background scheduler
from apscheduler.schedulers.background import BackgroundScheduler

# --- 1. Base Graph (with all locations) ---
city_graph = {
    'Koramangala': [('Silk Board', 10), ('Marath_W', 25), ('Indiranagar', 20), ('Jayanagar', 20)],
    'Silk Board': [('Koramangala', 10), ('Marath_E', 15), ('Elec_City', 20), ('Jayanagar', 15), ('Majestic', 40)],
    'Marath_W': [('Koramangala', 25), ('Marath_E', 5), ('Hebbal', 30), ('Indiranagar', 25)], 
    'Marath_E': [('Silk Board', 15), ('Marath_W', 5), ('Whitefield', 45)],
    'Hebbal': [('Marath_W', 30), ('Yeshwantpur', 10)],
    'Elec_City': [('Silk Board', 20)],
    'Yeshwantpur': [('Hebbal', 10), ('Majestic', 15)],
    'Majestic': [('Yeshwantpur', 15), ('Silk Board', 40)],
    'Indiranagar': [('Koramangala', 20), ('Marath_W', 25)],
    'Whitefield': [('Marath_E', 45)],
    'Jayanagar': [('Silk Board', 15), ('Koramangala', 20)]
}

# --- 2. Dijkstra's Algorithm ---
def find_fastest_route(graph, start, end):
    """Finds the fastest route using Dijkstra's algorithm with a min-heap."""
    priority_queue = [(0, start, [start])] # (time, node, path)
    visited = set()
    
    while priority_queue:
        (time, current_node, path) = heapq.heappop(priority_queue)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        if current_node == end:
            return (time, path) # Found it!
            
        if current_node in graph:
            for neighbor, travel_time in graph[current_node]:
                if neighbor not in visited:
                    new_time = time + travel_time
                    new_path = path + [neighbor]
                    heapq.heappush(priority_queue, (new_time, neighbor, new_path))
                    
    return (float('inf'), []) # No path found

# --- 3. Smart Intersection Class ---
class SmartIntersection:
    def __init__(self, name):
        self.name = name
        self.incoming_lanes = {}

    def add_incoming_road(self, road_name):
        self.incoming_lanes[road_name] = deque()

    def add_car(self, road_name):
        if road_name in self.incoming_lanes:
            self.incoming_lanes[road_name].append('car')

    def get_congestion_level(self, road_name):
        return len(self.incoming_lanes.get(road_name, []))

    def run_signal_cycle(self):
        """Simulates a green light, clearing 10 cars from the longest queue."""
        if not self.incoming_lanes: return
        
        longest_lane_name = max(self.incoming_lanes, 
                                key=lambda road: len(self.incoming_lanes[road]))
        
        cars_passed = 0
        for _ in range(10):
            if self.incoming_lanes[longest_lane_name]:
                self.incoming_lanes[longest_lane_name].popleft()
                cars_passed += 1
        
        if cars_passed > 0:
            print(f"[{self.name}]: Green light for '{longest_lane_name}', {cars_passed} cars passed.")

# --- 4. The Main Optimizer Class (The "Brain") ---
class TrafficOptimizer:
    def __init__(self, base_graph):
        self.base_graph = base_graph
        self.live_graph = copy.deepcopy(base_graph)
        self.intersections = {}

        for junction_name in base_graph:
            self.intersections[junction_name] = SmartIntersection(junction_name)

        for start_node, edges in base_graph.items():
            for end_node, _ in edges:
                road_name = f"{start_node}_to_{end_node}"
                self.intersections[end_node].add_incoming_road(road_name)

    def update_traffic_weights(self):
        """THE FEEDBACK LOOP: Updates the live_graph based on queue lengths."""
        print("...Updating live traffic weights...")
        new_live_graph = copy.deepcopy(self.base_graph)
        
        for start_node, edges in new_live_graph.items():
            for i, (end_node, base_time) in enumerate(edges):
                road_name = f"{start_node}_to_{end_node}"
                destination_intersection = self.intersections[end_node]
                congestion = destination_intersection.get_congestion_level(road_name)
                
                # Algorithm: Add 1 minute of delay for every 5 cars
                delay = congestion // 5
                new_live_graph[start_node][i] = (end_node, base_time + delay)
        
        self.live_graph = new_live_graph

    def simulate_traffic_flow(self):
        """Simulates new cars arriving at intersections."""
        print("...Simulating new traffic...")
        for _ in range(3): # Add 3 bursts of traffic
            start_node = random.choice(list(self.base_graph.keys()))
            if not self.base_graph[start_node]: continue
            
            end_node, _ = random.choice(self.base_graph[start_node])
            car_count = random.randint(5, 20)
            
            road_name = f"{start_node}_to_{end_node}"
            for _ in range(car_count):
                self.intersections[end_node].add_car(road_name)
            
            print(f"  Added {car_count} cars to '{road_name}'")

    def run_all_signals(self):
        """Simulates one cycle of all traffic lights."""
        print("...Running city signal cycles...")
        for junction in self.intersections.values():
            junction.run_signal_cycle()

# --- 5. Flask API Setup ---
app = Flask(__name__)
CORS(app) 

# --- 6. Create ONE Global Optimizer Instance ---
print("Initializing Bengaluru Traffic Optimizer...")
optimizer = TrafficOptimizer(city_graph)

# --- 7. Define Background Tasks ---
def background_task_simulator():
    """This function will be run by the scheduler."""
    optimizer.simulate_traffic_flow()
    optimizer.run_all_signals()

def background_task_updater():
    """This function updates the weights based on the simulation."""
    optimizer.update_traffic_weights()

# --- 8. API Endpoints ---
@app.route('/api/get-route', methods=['GET'])
def get_route():
    start_point = request.args.get('start')
    end_point = request.args.get('end')

    if not start_point or not end_point:
        return jsonify({"error": "Missing 'start' or 'end' parameter"}), 400

    # Use the 'live_graph' from our global 'optimizer' object
    (time, path) = find_fastest_route(optimizer.live_graph, start_point, end_point)

    if time == float('inf'):
        return jsonify({"error": f"No path found from {start_point} to {end_point}"}), 404

    response_data = {
        "start": start_point,
        "end": end_point,
        "time_minutes": time,
        "path": path
    }
    return jsonify(response_data)
    
@app.route('/api/get-all-traffic', methods=['GET'])
def get_all_traffic():
    """
    Sends the entire live graph to the frontend for visualization.
    """
    all_roads = []
    base_graph = optimizer.base_graph
    live_graph = optimizer.live_graph
    
    for start_node, edges in live_graph.items():
        for i, (end_node, live_time) in enumerate(edges):
            # Find the matching base_time for comparison
            base_time = -1
            for (base_end, base_t) in base_graph[start_node]:
                if base_end == end_node:
                    base_time = base_t
                    break
            
            road_data = {
                "start": start_node,
                "end": end_node,
                "live_time": live_time,
                "base_time": base_time
            }
            all_roads.append(road_data)
            
    return jsonify({"roads": all_roads})

# --- 9. Main Server Start ---
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    # Run simulation every 5 seconds
    scheduler.add_job(background_task_simulator, 'interval', seconds=5) 
    # Update graph weights every 10 seconds
    scheduler.add_job(background_task_updater, 'interval', seconds=10) 
    scheduler.start()
    print("Background scheduler started. Traffic simulation is LIVE.")
    
    # IMPORTANT: debug=False is required for the scheduler to work properly
    print("Starting Flask server on http://1.2.3.4:5000") # Use your server's IP
    # You must host on '0.0.0.0' to make it accessible to the public
    app.run(debug=False, host='0.0.0.0', port=5000) 