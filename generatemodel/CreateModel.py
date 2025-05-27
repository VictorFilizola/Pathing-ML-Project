import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from geopy.distance import geodesic
import random
import os

#Function to compute distance matrix
def compute_distance_matrix(coords):
    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i][j] = geodesic(coords[i], coords[j]).km
    return matrix

#Function to compute the problem's length
def compute_tsp_length(coords):
    from ortools.constraint_solver import routing_enums_pb2, pywrapcp
    n = len(coords)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return int(geodesic(coords[manager.IndexToNode(from_index)], coords[manager.IndexToNode(to_index)]).km * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_params)
    if not solution:
        return None

    index = routing.Start(0)
    total_distance = 0
    while not routing.IsEnd(index):
        next_index = solution.Value(routing.NextVar(index))
        total_distance += geodesic(coords[manager.IndexToNode(index)], coords[manager.IndexToNode(next_index)]).km
        index = next_index
    return total_distance

#Load dataset
data = pd.read_csv('../data/large.csv', header=None)
coords_list = data.values.tolist()

#Prepare dataset: for each sample, randomly select N points, compute TSP length
X = []
y = []

#number of training samples: subset of 5-10 locations
for _ in range(200):  
    subset = random.sample(coords_list, random.randint(5, 10))  
    length = compute_tsp_length(subset)
    if length is None:
        continue
    #feature: number of locations
    #target: route length in km
    X.append([len(subset)])  
    y.append(length)         

#Train a simple regression model
model = LinearRegression()
model.fit(X, y)

#Save the model in the 'models' folder
models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models'))
model_path = os.path.join(models_dir, 'pathing_model.pkl')
joblib.dump(model, model_path)

print(f"Model trained and saved as '{model_path}'")