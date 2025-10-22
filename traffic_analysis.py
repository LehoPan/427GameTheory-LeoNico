import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

def read_graph(file_path):
    try:
        G = nx.read_gml(file_path)
        if not nx.is_directed(G):
            G = G.to_directed()
        return G
    except Exception as e:
        sys.exit(f"Error reading graph: {e}")

def path_cost(G, path, flow):
    """Compute total cost of a path given edge flows."""
    cost = 0
    for u, v in zip(path[:-1], path[1:]):
        a = G[u][v].get("a", 0)
        b = G[u][v].get("b", 0)
        x = flow.get((u, v), 0)
        cost += a * x + b
    return cost

def compute_social_optimum(G, paths, n):
    """Minimize total system cost."""
    def total_cost(x):
        # x[i] = number of vehicles on path i
        edge_flow = {}
        for i, path in enumerate(paths):
            for u, v in zip(path[:-1], path[1:]):
                edge_flow[(u, v)] = edge_flow.get((u, v), 0) + x[i]
        return sum((G[u][v]["a"] * f + G[u][v]["b"]) * f for (u,v), f in edge_flow.items())

    cons = [{"type": "eq", "fun": lambda x: np.sum(x) - n}]
    bounds = [(0, n)] * len(paths)
    x0 = np.full(len(paths), n / len(paths))
    res = minimize(total_cost, x0, bounds=bounds, constraints=cons)
    return res.x if res.success else None

def plot_graph(G):
    pos = nx.spring_layout(G)
    labels = { (u, v): f"{G[u][v]['a']}x+{G[u][v]['b']}" for u, v in G.edges }
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

def plot_cost_functions(G):
    for u, v in G.edges:
        a, b = G[u][v]["a"], G[u][v]["b"]
        x = np.linspace(0, 10, 100)
        plt.plot(x, a*x + b, label=f"{u}->{v}")
    plt.xlabel("x (vehicles)")
    plt.ylabel("Cost")
    plt.legend()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("n", type=int)
    parser.add_argument("initial")
    parser.add_argument("final")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    G = read_graph(args.file)
    paths = list(nx.all_simple_paths(G, args.initial, args.final))
    print("Paths:", paths)

    # Compute Social Optimum
    opt_flows = compute_social_optimum(G, paths, args.n)
    print("Social Optimum Path Flows:", opt_flows)

    # TODO: Implement Nash Equilibrium (iterative adjustment)
    # ...

    if args.plot:
        plot_graph(G)
        plot_cost_functions(G)

if __name__ == "__main__":
    main()
