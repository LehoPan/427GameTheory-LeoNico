import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("n", type=int)
    parser.add_argument("initial")
    parser.add_argument("final")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    try:
        G = nx.read_gml(args.file)
        if not nx.is_directed(G):
            G = G.to_directed()
    except Exception as e:
        sys.exit(f"Error reading graph: {e}")

    paths = list(nx.all_simple_paths(G, args.initial, args.final))
    print("Paths:", paths)

    # if args.plot:
    #     plot_graph(G)
    #     plot_cost_functions(G)

if __name__ == "__main__":
    main()
