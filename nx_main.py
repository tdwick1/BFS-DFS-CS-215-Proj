import osmnx as ox
import networkx as nx
import random
import time
from collections import deque

WEIGHT_ATTR = "travel_time"

def build_osmnx_graph():
    print("Downloading Huntington road graph...")

    G = ox.graph_from_place(
        "Huntington, West Virginia, USA",
        network_type="drive_service"
    )

    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    # convert MultiDiGraph to DiGraph so edges are easier to work with
    G = ox.convert.to_digraph(G, weight="travel_time")

    # save original travel times for dynamic testing
    for u, v, data in G.edges(data=True):
        data["default_time"] = data.get("travel_time", 1)

    print("Graph created")
    print("Nodes:", len(G.nodes))
    print("Edges:", len(G.edges))

    return G


def get_start_end_nodes(G):
    # rough Huntington coordinates
    marshall_lat = 38.422
    marshall_lon = -82.429

    downtown_lat = 38.4192
    downtown_lon = -82.4452

    start = ox.distance.nearest_nodes(G, marshall_lon, marshall_lat)
    end = ox.distance.nearest_nodes(G, downtown_lon, downtown_lat)

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
        return [], float("inf"), []

    best = current[:]
    best_cost = path_cost(G, best)

    tabu = [tuple(current)]
    history = [best_cost]

    for i in range(iterations):
        if dynamic and i % 10 == 0 and i != 0:
            make_dynamic_changes(G, amount=15)

            # weights changed, so recalculate the best path cost
            best_cost = path_cost(G, best)

        candidates = []

        for _ in range(candidates_per_iter):
            new_path = make_neighbor(G, current, start, goal)

            if new_path and new_path[0] == start and new_path[-1] == goal:
                if tuple(new_path) not in tabu:
                    candidates.append(new_path)

        if not candidates:
            history.append(best_cost)
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

    return best, best_cost, history

def make_dynamic_changes(G, amount=15):
    # print("Changing travel times randomly...")

    for u, v, data in G.edges(data=True):
        default_time = data.get("default_time", data.get("travel_time", 1))

        min_time = max(0.1, default_time - amount)
        max_time = default_time + amount

        if random.random() < 0.1: 
            data["travel_time"] = random.uniform(min_time, max_time)


def time_algorithm(name, func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()

    print(name, "runtime:", round(end_time - start_time, 6), "seconds")
    return result


def main():
    G = build_osmnx_graph()

    sample_edge = list(G.edges(data=True))[0]
    print("Sample edge attributes:", sample_edge[2].keys())
    print("Using weight attribute:", WEIGHT_ATTR)
    print("Sample travel_time:", sample_edge[2].get(WEIGHT_ATTR))

    start, end = get_start_end_nodes(G)

    print("\nStart node:", start)
    print("End node:", end)

    print("\nSTATIC GRAPH TESTS")
    print("------------------")

    bfs_path = time_algorithm("BFS", bfs, G, start, end)
    dfs_path = time_algorithm("DFS", dfs, G, start, end)
    tabu_path, tabu_cost, tabu_history = time_algorithm(
        "Tabu Search",
        tabu_search,
        G,
        start,
        end
    )

    print("\nBFS path length:", len(bfs_path))
    print("BFS cost:", path_cost(G, bfs_path))

    print("\nDFS path length:", len(dfs_path))
    print("DFS cost:", path_cost(G, dfs_path))

    print("\nTabu path length:", len(tabu_path))
    print("Tabu cost:", tabu_cost)
    print("Tabu convergence start:", tabu_history[0])
    print("Tabu convergence end:", tabu_history[-1])

    print("\nDYNAMIC GRAPH TEST")
    print("------------------")

    # make_dynamic_changes(G, amount=15)
    print("Running Tabu Search while randomly changing edge weights during the search...")
    dynamic_tabu_path, dynamic_tabu_cost, dynamic_history = time_algorithm(
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

    print("\nDynamic Tabu path length:", len(dynamic_tabu_path))
    print("Dynamic Tabu cost:", dynamic_tabu_cost)
    print("Dynamic convergence start:", dynamic_history[0])
    print("Dynamic convergence end:", dynamic_history[-1])

def run_tests(num_trials=5):
    output_file = "test_results.txt"

    with open(output_file, "w") as f:
        for trial in range(1, num_trials + 1):
            print("\nTRIAL", trial)
            f.write("\nTRIAL " + str(trial) + "\n")

            G = build_osmnx_graph()
            start, end = get_start_end_nodes(G)

            bfs_path = time_algorithm("BFS", bfs, G, start, end)
            dfs_path = time_algorithm("DFS", dfs, G, start, end)
            tabu_path, tabu_cost, tabu_history = time_algorithm(
                "Tabu Search", tabu_search, G, start, end, 300, 20, 20
            )

            dynamic_tabu_path, dynamic_tabu_cost, dynamic_history = time_algorithm(
                "Dynamic Tabu Search", tabu_search, G, start, end, 300, 20, 20, True
            )

            results = f"""
Start node: {start}
End node: {end}

BFS path length: {len(bfs_path)}
BFS cost: {path_cost(G, bfs_path)}

DFS path length: {len(dfs_path)}
DFS cost: {path_cost(G, dfs_path)}

Tabu path length: {len(tabu_path)}
Tabu cost: {tabu_cost}
Tabu convergence start: {tabu_history[0]}
Tabu convergence end: {tabu_history[-1]}

Dynamic Tabu path length: {len(dynamic_tabu_path)}
Dynamic Tabu cost: {dynamic_tabu_cost}
Dynamic convergence start: {dynamic_history[0]}
Dynamic convergence end: {dynamic_history[-1]}

------------------------------
"""
            print(results)
            f.write(results)

    print("saved results to", output_file)



TEST = True

if __name__ == "__main__":
    if TEST:
        run_tests(num_trials=5)
    else:
        main()
