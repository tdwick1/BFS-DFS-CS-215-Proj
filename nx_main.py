import osmnx as ox
import networkx as nx
import random
import time
import tracemalloc
from collections import deque

WEIGHT_ATTR = "travel_time"

PLACES = [
    "Barboursville, West Virginia, USA",
    "Huntington, West Virginia, USA",
    "Charleston, West Virginia, USA",
    "Cabell County, West Virginia, USA",
    "Morgantown, West Virginia, USA"
]


def build_osmnx_graph(place_name):
    print(f"Downloading {place_name} road graph...")

    G = ox.graph_from_place(place_name, network_type="drive_service")

    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    G = ox.convert.to_digraph(G, weight=WEIGHT_ATTR)

    for u, v, data in G.edges(data=True):
        data["default_time"] = data.get(WEIGHT_ATTR, 1)

    print("Graph created")
    print("Nodes:", len(G.nodes))
    print("Edges:", len(G.edges))

    return G


def get_start_end_nodes(G, min_path_length=30):
    nodes = list(G.nodes)

    for _ in range(100):
        start = random.choice(nodes)
        end = random.choice(nodes)

        if start == end:
            continue

        test_path = bfs(G, start, end)

        if test_path and len(test_path) >= min_path_length:
            return start, end

    return start, end


def path_cost(G, path, weight_attr=WEIGHT_ATTR):
    if not path:
        return float("inf")

    total = 0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        if not G.has_edge(u, v):
            return float("inf")

        total += G[u][v].get(weight_attr, 1)

    return total


def bfs(G, start, goal):
    queue = deque([[start]])
    visited = set([start])

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal:
            return path

        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return []


def dfs(G, start, goal):
    stack = [[start]]
    visited = set()

    while stack:
        path = stack.pop()
        node = path[-1]

        if node == goal:
            return path

        if node in visited:
            continue

        visited.add(node)

        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                stack.append(path + [neighbor])

    return []


def dijkstra(G, start, goal):
    try:
        return nx.shortest_path(G, start, goal, weight=WEIGHT_ATTR)
    except nx.NetworkXNoPath:
        return []


def random_path(G, start, goal, max_steps=300):
    path = [start]
    current = start
    visited = set([start])

    for _ in range(max_steps):
        neighbors = [n for n in G.neighbors(current) if n not in visited]

        if not neighbors:
            break

        current = random.choice(neighbors)
        path.append(current)
        visited.add(current)

        if current == goal:
            return path

    return []


def make_neighbor(G, path, start, goal):
    if len(path) < 2:
        return bfs(G, start, goal)

    cut = random.randint(1, len(path) - 1)
    new_path = path[:cut]

    last = new_path[-1]
    rest = random_path(G, last, goal)

    if not rest:
        rest = bfs(G, last, goal)

    if not rest:
        return path

    return new_path[:-1] + rest


def tabu_search(G, start, goal, iterations=100, tabu_size=20, candidates_per_iter=10, dynamic=False):
    current = bfs(G, start, goal)

    if not current:
        return [], float("inf"), [], []

    best = current[:]
    best_cost = path_cost(G, best)

    tabu = [tuple(current)]
    history = [best_cost]
    path_history = [best[:]]

    for i in range(iterations):
        if dynamic and i % 10 == 0 and i != 0:
            make_dynamic_changes(G, amount=15)
            best_cost = path_cost(G, best)

        candidates = []

        for _ in range(candidates_per_iter):
            new_path = make_neighbor(G, current, start, goal)

            if new_path and new_path[0] == start and new_path[-1] == goal:
                if tuple(new_path) not in tabu:
                    candidates.append(new_path)

        if not candidates:
            history.append(best_cost)
            path_history.append(best[:])
            continue

        current = min(candidates, key=lambda p: path_cost(G, p))
        cost = path_cost(G, current)

        if cost < best_cost:
            best = current[:]
            best_cost = cost

        tabu.append(tuple(current))

        if len(tabu) > tabu_size:
            tabu.pop(0)

        history.append(best_cost)
        path_history.append(best[:])

    return best, best_cost, history, path_history


def make_dynamic_changes(G, amount=15):
    for u, v, data in G.edges(data=True):
        default_time = data.get("default_time", data.get(WEIGHT_ATTR, 1))

        min_time = max(0.1, default_time - amount)
        max_time = default_time + amount

        if random.random() < 0.1:
            data[WEIGHT_ATTR] = random.uniform(min_time, max_time)


def time_algorithm(name, func, *args):
    tracemalloc.start()

    start_time = time.time()
    result = func(*args)
    end_time = time.time()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    runtime = round(end_time - start_time, 6)
    memory_mb = round(peak / 1024 / 1024, 4)

    print(name, "runtime:", runtime, "seconds")
    print(name, "peak memory:", memory_mb, "MB")

    return result, runtime, memory_mb


def path_to_latlong(G, path):
    coords = []

    for node in path:
        lat = G.nodes[node]["y"]
        lon = G.nodes[node]["x"]
        coords.append((lat, lon))

    return coords


def run_tests(num_trials=5):
    for place in PLACES:
        print(f"\nTesting on {place}...")

        base_G = build_osmnx_graph(place)
        node_count = len(base_G.nodes)
        edge_count = len(base_G.edges)
        if place == "Huntington, West Virginia, USA":
            start, end = get_start_end_nodes(base_G, min_path_length=40)
        else:
            start, end = get_start_end_nodes(base_G)

        print(f"Running {num_trials} trials")
        print("Start node lat:", base_G.nodes[start]["y"], "lon:", base_G.nodes[start]["x"])
        print("End node lat:", base_G.nodes[end]["y"], "lon:", base_G.nodes[end]["x"])

        output_file = f"results_{place.replace(', ', '_').replace(' ', '_')}_{int(time.time())}.txt"

        with open(output_file, "w") as f:
            for trial in range(1, num_trials + 1):
                print("\nTRIAL", trial)
                f.write("\nTRIAL " + str(trial) + "\n")

                G = build_osmnx_graph(place)

                bfs_path, bfs_runtime, bfs_memory = time_algorithm("BFS", bfs, G, start, end)
                dfs_path, dfs_runtime, dfs_memory = time_algorithm("DFS", dfs, G, start, end)

                (tabu_path, tabu_cost, tabu_history, tabu_path_history), tabu_runtime, tabu_memory = time_algorithm(
                    "Tabu Search",
                    tabu_search,
                    G,
                    start,
                    end,
                    300,
                    20,
                    20
                )

                dijkstra_path = []
                dijkstra_cost = "N/A"
                dijkstra_runtime = "N/A"
                dijkstra_memory = "N/A"

                if place == "Huntington, West Virginia, USA":
                    dijkstra_path, dijkstra_runtime, dijkstra_memory = time_algorithm(
                        "Dijkstra",
                        dijkstra,
                        G,
                        start,
                        end
                    )
                    dijkstra_cost = path_cost(G, dijkstra_path)

                # save static costs BEFORE dynamic tabu modifies the graph
                bfs_cost = path_cost(G, bfs_path)
                dfs_cost = path_cost(G, dfs_path)
                static_tabu_cost = tabu_cost

                (dynamic_tabu_path, dynamic_tabu_cost, dynamic_history, dynamic_path_history), dynamic_runtime, dynamic_memory = time_algorithm(
                    "Dynamic Tabu Search",
                    tabu_search,
                    G,
                    start,
                    end,
                    300,
                    20,
                    20,
                    True
                )

                results = f"""
Map: {place}
Nodes: {node_count}
Edges: {edge_count}
Start node: {start}
End node: {end}

BFS path length: {len(bfs_path)}
BFS cost: {bfs_cost}
BFS runtime: {bfs_runtime} seconds
BFS peak memory: {bfs_memory} MB

DFS path length: {len(dfs_path)}
DFS cost: {dfs_cost}
DFS runtime: {dfs_runtime} seconds
DFS peak memory: {dfs_memory} MB

Tabu path length: {len(tabu_path)}
Tabu cost: {static_tabu_cost}
Tabu runtime: {tabu_runtime} seconds
Tabu peak memory: {tabu_memory} MB
Tabu convergence start: {tabu_history[0]}
Tabu convergence end: {tabu_history[-1]}

Dynamic Tabu path length: {len(dynamic_tabu_path)}
Dynamic Tabu cost: {dynamic_tabu_cost}
Dynamic Tabu runtime: {dynamic_runtime} seconds
Dynamic Tabu peak memory: {dynamic_memory} MB
Dynamic convergence start: {dynamic_history[0]}
Dynamic convergence end: {dynamic_history[-1]}

BFS path: {path_to_latlong(G, bfs_path)}
DFS path: {path_to_latlong(G, dfs_path)}
Tabu path: {path_to_latlong(G, tabu_path)}
Dynamic Tabu path: {path_to_latlong(G, dynamic_tabu_path)}

Tabu path history: {[path_to_latlong(G, p) for p in tabu_path_history[:10]]}
Dynamic Tabu path history: {[path_to_latlong(G, p) for p in dynamic_path_history[:10]]}
"""

                if place == "Huntington, West Virginia, USA":
                    results += f"""
Dijkstra path length: {len(dijkstra_path)}
Dijkstra cost: {dijkstra_cost}
Dijkstra runtime: {dijkstra_runtime} seconds
Dijkstra peak memory: {dijkstra_memory} MB
Dijkstra path: {path_to_latlong(G, dijkstra_path)}
"""

                results += "\n------------------------------\n"

                print(results)
                f.write(results)

        print("saved results to", output_file)


if __name__ == "__main__":
    run_tests(num_trials=5)