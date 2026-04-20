from graph import Graph
from algorithms import bfs, dfs, tabu_search


def build_graph():
    g = Graph()

    # sample graph for testing
    g.add_edge("A", "B", 4)
    g.add_edge("A", "C", 2)
    g.add_edge("C", "D", 3)
    g.add_edge("D", "B", 2)
    g.add_edge("B", "E", 5)
    g.add_edge("D", "E", 4)

    return g


def main():
    g = build_graph()

    start = "A"
    end = "E"

    print("before update:")
    p1 = bfs(g, start, end)
    p2 = dfs(g, start, end)
    p3, c3 = tabu_search(g, start, end)

    print("BFS:", p1, "cost:", g.path_cost(p1))
    print("DFS:", p2, "cost:", g.path_cost(p2))
    print("Tabu:", p3, "cost:", c3)

    print("\nupdating weights...")
    g.update_weight("D", "E", 20)

    p1 = bfs(g, start, end)
    p2 = dfs(g, start, end)
    p3, c3 = tabu_search(g, start, end)

    print("BFS:", p1, "cost:", g.path_cost(p1))
    print("DFS:", p2, "cost:", g.path_cost(p2))
    print("Tabu:", p3, "cost:", c3)


if __name__ == "__main__":
    main()
