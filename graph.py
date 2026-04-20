class Graph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u, v, w):
        self.add_node(u)
        self.add_node(v)

        self.adj[u].append((v, w))
        self.adj[v].append((u, w))  # undirected graph

    def neighbors(self, node):
        return self.adj.get(node, [])

    def update_weight(self, u, v, new_w):
        for i in range(len(self.adj[u])):
            if self.adj[u][i][0] == v:
                self.adj[u][i] = (v, new_w)

        for i in range(len(self.adj[v])):
            if self.adj[v][i][0] == u:
                self.adj[v][i] = (u, new_w)

    def get_weight(self, u, v):
        for n, w in self.adj.get(u, []):
            if n == v:
                return w
        return None

    def path_cost(self, path):
        total = 0
        for i in range(len(path) - 1):
            w = self.get_weight(path[i], path[i + 1])
            if w is None:
                return float("inf")
            total += w
        return total
