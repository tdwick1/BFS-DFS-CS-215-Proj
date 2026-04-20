from graph import Graph
from algorithms import bfs, dfs, tabu_search


def build_graph():
    g = Graph()

    # Huntington-style road network
    g.add_edge("Marshall University", "3rd Ave", 2)
    g.add_edge("Marshall University", "Hal Greer Blvd", 4)
    g.add_edge("3rd Ave", "5th Ave", 3)
    g.add_edge("5th Ave", "Hal Greer Blvd", 2)
    g.add_edge("Hal Greer Blvd", "Downtown Huntington", 5)
    g.add_edge("5th Ave", "Downtown Huntington", 4)

    return g


def main():
    g = build_graph()

    start = "Marshall University"
    end = "Downtown Huntington"

    print("before update:")
    p1 = bfs(g, start, end)
    p2 = dfs(g, start, end)
    p3, c3 = tabu_search(g, start, end)

    print("BFS:", p1, "cost:", g.path_cost(p1))
    print("DFS:", p2, "cost:", g.path_cost(p2))
    print("Tabu:", p3, "cost:", c3)

    # simulate traffic (road gets worse)
    print("\nupdating weights (traffic on 5th Ave -> Downtown)...")
    g.update_weight("5th Ave", "Downtown Huntington", 20)

    p1 = bfs(g, start, end)
    p2 = dfs(g, start, end)
    p3, c3 = tabu_search(g, start, end)

    print("BFS:", p1, "cost:", g.path_cost(p1))
    print("DFS:", p2, "cost:", g.path_cost(p2))
    print("Tabu:", p3, "cost:", c3)


if __name__ == "__main__":
    main()