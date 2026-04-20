# CS 215 Project – Graph Search and Optimization

## Overview

This project models a road network as a weighted graph and compares different search algorithms:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Tabu Search (optimization algorithm)

The goal is to analyze how these algorithms behave on a dynamic weighted graph, where edge weights (road costs) can change over time (ex: traffic).

---

## How It Works

- Nodes represent locations (intersections or roads)
- Edges represent connections with weights (distance, traffic, etc.)
- The graph supports dynamic updates, meaning weights can change

---

## Algorithms

### BFS (Breadth-First Search)

- Finds a path with the fewest edges
- Does NOT consider weights
- Good for simple traversal

### DFS (Depth-First Search)

- Explores deeply before backtracking
- Does NOT consider weights
- Path found depends on traversal order

### Tabu Search

- Metaheuristic optimization algorithm
- Attempts to find a low-cost path
- Uses a tabu list to avoid repeating bad solutions
- Works better for weighted graphs

---

## Example Output

Before updating weights:

BFS: ['A', 'B', 'E'] cost: 9
DFS: ['A', 'C', 'D', 'E'] cost: 9
Tabu: ['A', 'C', 'D', 'E'] cost: 9

After increasing weight of edge D-E:

BFS: ['A', 'B', 'E'] cost: 9
DFS: ['A', 'C', 'D', 'E'] cost: 25
Tabu: ['A', 'B', 'E'] cost: 9

---

## Analysis

- BFS and DFS do not adjust to weight changes because they do not optimize for cost
- DFS continued using a now-expensive path
- Tabu Search adapted and found a better path after the graph changed

This demonstrates that:
Tabu Search is more effective for optimization in dynamic weighted graphs

---

## How to Run

python main.py

---

## Notes

- BFS and DFS are included for comparison purposes
- Tabu Search is the main optimization method used in this project
