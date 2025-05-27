import tkinter as tk
from tkinter import messagebox, filedialog
from geopy.geocoders import Nominatim
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
from shapely.geometry import Point, LineString
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from geopy.distance import geodesic
import threading
import os
from datetime import datetime

def compute_distance_matrix(coords):
    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i][j] = geodesic(coords[i], coords[j]).km
    return matrix

def solve_tsp(distance_matrix):
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return int(distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)] * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_params)
    if not solution:
        raise Exception("No solution found!")

    index = routing.Start(0)
    route = []
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(route[0]) 
    return route

def plot_route_with_map(coords, route, location_names, filename=None):
    if filename is None:
        # Generate filename with current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"GeneratedPathing_{current_date}.pdf"

    # Ensure the file is saved in the "models" directory
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../outputs'))
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    filepath = os.path.join(models_dir, filename)

    points = [Point(coords[i][1], coords[i][0]) for i in route]
    gdf_points = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
    line = LineString(points)
    gdf_line = gpd.GeoDataFrame(geometry=[line], crs="EPSG:4326")

    gdf_points = gdf_points.to_crs(epsg=3857)
    gdf_line = gdf_line.to_crs(epsg=3857)

    fig = plt.figure(figsize=(10, 12))

    # Create table at top 30% of figure
    ax_table = fig.add_axes([0.1, 0.7, 0.8, 0.25]) 
    ax_table.axis('off')

    visit_order = list(range(1, len(route) + 1))
    ordered_names = [location_names[i] for i in route]
    table_data = list(zip(visit_order, ordered_names))

    col_labels = ['Visit Order', 'Address']
    table = ax_table.table(cellText=table_data, colLabels=col_labels, cellLoc='left', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # Create map at bottom 70% of figure
    ax_map = fig.add_axes([0.05, 0.05, 0.9, 0.6])

    gdf_line.plot(ax=ax_map, linewidth=3, alpha=0.7, color='blue')
    gdf_points.plot(ax=ax_map, color='red', markersize=50)

    for i, point in enumerate(gdf_points.geometry):
        ax_map.annotate(str(i+1), xy=(point.x, point.y), xytext=(3,3), textcoords="offset points", fontsize=12, color='black')

    ctx.add_basemap(ax_map, source=ctx.providers.OpenStreetMap.Mapnik)

    ax_map.set_axis_off()
    plt.title('Optimal Route on Map')

    plt.savefig(filepath, dpi=300)
    plt.close()

#create GUI
class RouteApp:
    def __init__(self, root):
        self.root = root
        root.title("Route Planner")

        self.label = tk.Label(root, text="Enter addresses (one per line):")
        self.label.pack()

        self.text = tk.Text(root, width=60, height=15)
        self.text.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.run_button = tk.Button(self.button_frame, text="Generate Route PDF", command=self.run)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack()

        self.geolocator = Nominatim(user_agent="route_planner_app")

    def geocode_addresses(self, addresses):
        coords = []
        for addr in addresses:
            addr = addr.strip()
            if not addr:
                continue
            try:
                location = self.geolocator.geocode(addr)
                if location is None:
                    raise ValueError(f"Address not found: {addr}")
                coords.append((location.latitude, location.longitude))
            except Exception as e:
                raise ValueError(f"Error geocoding '{addr}': {e}")
        return coords

    def run(self):
        threading.Thread(target=self._run).start()

    def _run(self):
        self.status_label.config(text="Geocoding addresses...")
        addresses = self.text.get("1.0", tk.END).strip().split("\n")
        try:
            coords = self.geocode_addresses(addresses)
            if len(coords) < 2:
                messagebox.showerror("Error", "Please enter at least two valid addresses.")
                self.status_label.config(text="")
                return

            self.status_label.config(text="Computing optimal route...")
            dist_matrix = compute_distance_matrix(coords)
            route = solve_tsp(dist_matrix)

            self.status_label.config(text="Generating PDF...")
            plot_route_with_map(coords, route, addresses)

            messagebox.showinfo("Success", "Route PDF generated as 'route_map.pdf'")
            self.status_label.config(text="Done!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = RouteApp(root)
    root.mainloop()
