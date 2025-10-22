import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
import random

def read_graph(file_path):
    try:
        G = nx.read_gml(file_path)
        if not nx.is_directed(G):
            G = G.to_directed()
        return G
    except Exception as e:
        sys.exit(f"Error reading graph: {e}")

def path_cost(G, path, edge_flow):
    """Compute total cost of a path given edge flows."""
    cost = 0
    for u, v in zip(path[:-1], path[1:]):
        a = G[u][v].get("a", 0)
        b = G[u][v].get("b", 0)
        x = edge_flow.get((u, v), 0)
        cost += a * x + b
    return cost

def compute_social_optimum(G, paths, n):
    """Minimize total system cost (continuous)."""
    def total_cost(x):
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

def compute_nash_equilibrium(G, paths, n, max_iter=1000):
    """Compute discrete (atomic) Nash equilibrium via best-response dynamics."""
    # Random initial assignment of each vehicle to a path
    assignments = [random.randint(0, len(paths) - 1) for _ in range(n)]

    for iteration in range(max_iter):
        changed = False
        # Compute edge flow
        edge_flow = {}
        for i in range(n):
            path = paths[assignments[i]]
            for u, v in zip(path[:-1], path[1:]):
                edge_flow[(u, v)] = edge_flow.get((u, v), 0) + 1

        # Each player checks if switching paths would lower their cost
        for i in range(n):
            current_path = paths[assignments[i]]
            current_cost = path_cost(G, current_path, edge_flow)
            best_path_idx, best_cost = assignments[i], current_cost

            for j, path in enumerate(paths):
                if j == assignments[i]:
                    continue
                # simulate moving one vehicle
                tmp_flow = edge_flow.copy()
                for u, v in zip(current_path[:-1], current_path[1:]):
                    tmp_flow[(u, v)] -= 1
                for u, v in zip(path[:-1], path[1:]):
                    tmp_flow[(u, v)] = tmp_flow.get((u, v), 0) + 1
                c = path_cost(G, path, tmp_flow)
                if c < best_cost - 1e-6:
                    best_path_idx, best_cost = j, c

            if best_path_idx != assignments[i]:
                assignments[i] = best_path_idx
                changed = True

        if not changed:
            print(f"Converged after {iteration+1} iterations.")
            break

    # Count how many vehicles use each path
    path_flows = [assignments.count(i) for i in range(len(paths))]
    return path_flows

def plot_graph(G):
    pos = nx.spring_layout(G)
    labels = {(u, v): f"{G[u][v]['a']}x+{G[u][v]['b']}" for u, v in G.edges}
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
    print("Social Optimum Path Flows:", np.round(opt_flows, 2))

    # Compute Nash Equilibrium (discrete atomic)
    nash_flows = compute_nash_equilibrium(G, paths, args.n)
    print("Nash Equilibrium Path Flows:", nash_flows)

    if args.plot:
        plot_graph(G)
        plot_cost_functions(G)

if __name__ == "__main__":
    main()
