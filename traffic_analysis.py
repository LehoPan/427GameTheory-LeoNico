import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import cvxpy as cp

def path_cost(G, path, flow):
    """Compute total cost of a path given edge flows."""
    cost = 0
    for u, v in zip(path[:-1], path[1:]):
        a = G[u][v].get("a", 0)
        b = G[u][v].get("b", 0)
        x = flow.get((u, v), 0)
        cost += a * x + b
    return cost

# Computes the social optimum of the graph for n drivers
def compute_social_optimum(G, paths, n):
    # Uses cvxpy to do convex matrix multiplication 
    # Instead of brute forcing all paths to find the social optimum
    edge_list = list(G.edges())
    incidence = np.zeros((len(edge_list), len(paths)))
    for j, path in enumerate(paths):
        for u, v in zip(path[:-1], path[1:]):
            incidence[edge_list.index((u, v)), j] = 1

    a = np.array([G[u][v]["a"] for (u, v) in edge_list])
    b = np.array([G[u][v]["b"] for (u, v) in edge_list])

    f = cp.Variable(len(paths), integer=True)
    x = incidence @ f

    objective = cp.Minimize(cp.sum(a @ cp.square(x) + b @ x))
    constraints = [cp.sum(f) == n, f >= 0]

    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS_BB)

    # Returns a list with how many drivers used each path, index aligned
    # and the calculated social optimum
    return np.round(f.value), round(prob.value)

# Plots two graphs, one for the social optimum and another for the equilibrium, each edge displays how many drivers used it.
def plot_graph(G, paths, social_optimums):
    # calculates how many drivers use each edge
    driver_flow = {}
    for i in range(len(paths)):
        for j in range(len(paths[i]) - 1):
            try:
                driver_flow[(paths[i][j], paths[i][j+1])]
            except:
                driver_flow[(paths[i][j], paths[i][j+1])] = 0
            driver_flow[(paths[i][j], paths[i][j+1])] += social_optimums[i]
    pos = nx.spring_layout(G)
    # Plots the nodes and edges, along with a label on each edge for how many driver utilize it.
    labels = { (u, v): f"DriverFlow={driver_flow[(u,v)]}" for u,v in G.edges }
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

def main():
    # Reads arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("n", type=int)
    parser.add_argument("initial")
    parser.add_argument("final")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    # Reads in the input graph .gml file
    try:
        G = nx.read_gml(args.file)
        if not nx.is_directed(G):
            G = G.to_directed()
    except Exception as e:
        sys.exit(f"Error reading graph: {e}")

    # Computes all paths from the initial to final node
    paths = list(nx.all_simple_paths(G, args.initial, args.final))

    # Compute Social Optimum and display each path in columns
    print("\n______Social Optimum______\n")
    driver_path_count, social_optimum = compute_social_optimum(G, paths, args.n)
    print("Social Optimum is:", social_optimum)
    print("Paths of Drivers:")
    # Formats into columns
    print(f"{'Drivers':>5} {'Path':>5}")
    for drive, path, in zip(driver_path_count, paths):
        space = 11 - len(str(drive))
        print(f"{drive:<{space}} {str(path):>5}")

    # TODO: Implement Nash Equilibrium (iterative adjustment)
    # ...

    # Plots two graphs, one for social and another for equilibrium
    if args.plot:
        plot_graph(G, paths, driver_path_count)

if __name__ == "__main__":
    main()
