# BFS-DFS-CS-215-Proj

Small CS project using a weighted graph with BFS, DFS, and a simple Tabu Search.

## Files
- `graph.py` - graph structure and weight updates
- `algorithms.py` - BFS, DFS, random path generation, and tabu search
- `main.py` - test runner with a sample graph

## Run
```bash
python main.py
```

## Notes
- BFS and DFS can traverse a weighted graph, but they do not optimize total weight.
- Tabu search is being used here as the path optimization part.
- Edge weights can be updated to simulate changing traffic or road conditions.
