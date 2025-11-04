AptRouteBLR 🚦

A Dynamic Traffic Simulation & Proactive Routing System for Bengaluru

AptRouteBLR is a web-based application designed to combat Bengaluru's traffic congestion by providing optimal travel routes based on a live, self-correcting traffic simulation.

Unlike traditional reactive navigation tools that rely on historical data or simple user GPS pings, AptRouteBLR is proactive. It functions as a simulation engine, modeling the root causes of congestion—such as queue lengths at signals—to predict delays before they fully form. This allows it to route users around the cause of a jam, not just the symptom.

📋 Table of Contents

Live Demo Features

How It Works: The Dynamic Feedback Loop

Technology Stack

🛠️ Installation & Setup

Project Files

Future Enhancements

🚀 Live Demo Features

The fully functional prototype (index.html) demonstrates the core concept with:

Interactive Map: A clean UI built with Leaflet.js showing key Bengaluru junctions.

Dynamic Route Selection: Users can select a start and end point from dropdown menus.

Live Traffic Visualization: The map displays all roads with color-coded traffic conditions (Green/Yellow/Red), which are updated every 10 seconds from the backend.

Real-Time Route Calculation: The optimal path and estimated travel time are calculated and displayed instantly based on the live simulation.

⚙️ How It Works: The Dynamic Feedback Loop

The system's "brain" is the Flask backend (app.py), which runs a continuous, circular feedback loop to keep traffic data alive.

1. Backend Simulation Engine (app.py)

A powerful Flask server acts as the central API.

On startup, it initializes an TrafficOptimizer object with a static city_graph (base travel times).

It uses APScheduler to run two background tasks continuously:

simulate_traffic_flow(): This function "creates" new cars and adds them to virtual queues (collections.deque) at "Smart Intersections."

run_all_signals(): This function simulates traffic lights clearing a set number of cars from the longest queues.

2. The Dynamic Feedback Loop (app.py)

This is the system's most innovative feature, run by the update_traffic_weights() function every 10 seconds.

It measures the simulated congestion (i.e., the len() of the car queues) at every intersection.

It calculates a real-time delay penalty for each road based on this congestion (e.g., +1 minute for every 5 cars in the queue).

It generates a new live_graph by adding these real-time delays to the base travel times.

3. Frontend Routing Request (script.js)

When the user selects a start and end point in index.html, the frontend calls the /api/get-route endpoint.

4. Smart Routing (app.py)

The backend's find_fastest_route function runs Dijkstra's Algorithm (optimized with a heapq min-priority queue) on the current live_graph, not the static one.

This ensures the path returned is the fastest at that exact moment, dynamically accounting for all simulated traffic jams.

💻 Technology Stack

This project is built on a foundation of classic and efficient data structures and algorithms.

Backend

Python

Flask: Powers the web server and API endpoints (/api/get-route, /api/get-all-traffic).

APScheduler: A background scheduler to run the simulation and graph updates continuously.

Flask-CORS: Handles cross-origin requests from the frontend.

Frontend

HTML5

CSS3 (with a modern, responsive design).

JavaScript (ES6+)

Leaflet.js: The core library for the interactive map visualization.

Core Data Structures & Algorithms (in app.py)

Graphs (Adjacency List): The city_graph and live_graph are represented as weighted graphs using Python dictionaries.

Dijkstra's Algorithm: The core algorithm in find_fastest_route used to find the fastest path in the weighted live_graph.

Priority Queue (Min-Heap): Python's heapq module is used to implement Dijkstra's algorithm efficiently.

Queues (FIFO): The SmartIntersection class uses collections.deque to simulate a First-In, First-Out line of cars at a traffic light.

Hash Maps (Dictionaries): Used for all critical $O(1)$ average-time lookups (e.g., mapping junction names to their SmartIntersection objects).

🛠️ Installation & Setup

To run this project locally:

Clone the Repository

git clone [https://github.com/deveshreddyp/AptRouteBLR.git](https://github.com/deveshreddyp/AptRouteBLR.git)
cd AptRouteBLR


Set up a Python Virtual Environment

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate


Install Backend Dependencies
All required Python packages are listed in requirements.txt.

pip install -r requirements.txt


Run the Backend Server
This will start the Flask server and activate the background simulation scheduler.

python app.py


The server will be running on http://127.0.0.1:5000/.

Launch the Frontend
No build step is required. Simply open the index.html file directly in your web browser. The app will connect to the running backend automatically.

🗂️ Project Files

app.py: The core Flask backend, containing all simulation logic, API endpoints, and data structures.

index.html: The main frontend file containing the HTML structure of the web app.

script.js: All frontend JavaScript for map rendering (Leaflet.js), user interaction, and API calls.

style.css: All CSS rules for styling the web application.

requirements.txt: A list of all Python dependencies for the backend.

report.pdf: A detailed project report outlining the problem, solution, and technical implementation.

Bangalore FlowFast (1).pptx: A presentation slide deck summarizing the project's goals, architecture, and innovation.

📈 Future Enhancements

The prototype successfully proves the concept. Future work would focus on moving from simulation to real-world application:

Integrate Real-World Data: Replace the random car generator with live data feeds from traffic cameras or IoT sensors to "seed" the simulation.

Expand the City Graph: Scale the city_graph to include a more granular map of Bengaluru's neighborhoods and arterial roads.

Develop a Mobile Application: Create native iOS and Android apps for on-the-go use with turn-by-turn directions.