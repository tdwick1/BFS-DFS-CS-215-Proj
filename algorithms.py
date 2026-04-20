from collections import deque
import random


def bfs(graph, start, goal):
    queue = deque([[start]])
    visited = set([start])

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal:
            return path

        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return []


def dfs(graph, start, goal):
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

        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                stack.append(path + [neighbor])

    return []


def random_path(graph, start, goal):
    path = [start]
    current = start
    visited = set([start])

    for _ in range(50):
        neighbors = [n for n, _ in graph.neighbors(current) if n not in visited]
        if not neighbors:
            break

        current = random.choice(neighbors)
        path.append(current)
        visited.add(current)

        if current == goal:
            return path

    return []


def make_neighbor(graph, path, start, goal):
    if len(path) < 2:
        return random_path(graph, start, goal)

    cut = random.randint(1, len(path) - 1)
    new_path = path[:cut]

    last = new_path[-1]
    rest = random_path(graph, last, goal)

    if not rest:
        return path

    return new_path[:-1] + rest


def tabu_search(graph, start, goal):
    current = random_path(graph, start, goal)
    if not current:
        return [], float("inf")

    best = current[:]
    best_cost = graph.path_cost(best)

    tabu = [tuple(current)]

    for _ in range(200):
        candidates = []

        for _ in range(10):
            new_path = make_neighbor(graph, current, start, goal)
            if new_path and tuple(new_path) not in tabu:
                candidates.append(new_path)

        if not candidates:
            continue

        current = min(candidates, key=lambda p: graph.path_cost(p))
        cost = graph.path_cost(current)

        if cost < best_cost:
            best = current[:]
            best_cost = cost

        tabu.append(tuple(current))
        if len(tabu) > 20:
            tabu.pop(0)

    return best, best_cost
