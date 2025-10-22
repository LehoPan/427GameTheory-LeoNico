# 427GameTheory-LeoNico
By Leo Pan 030025552 and Nicolas Piker 029966545

## Dependencies
We installed and utilized the python `networkx`, `numpy`, `cvxpy ecos` and `matplotlib.pyplot` packages.

All packages are standard numpy installation but `cvxpy ecos` was finicky, so here is the install we used for it.

`pip install cvxpy ecos`

## Implementations
`Argparse` used to read command line arguments, and `networkx` for reading the input graph .gml.

We compute the Social Optimum by using the `cvxpy` library to help with the convex matric multiplication, which saves us from directly bruteforcing every driver path combination. The function returns a tuple with a list of how many drivers use each path, as well as the total social optimum.

The plot function looks at the drivers on each path for then social optimum, and calculates how mnay drivers use each edge between two nodes. Then adds the labels to each edge before doing it for the equilibrium as well. Then shows the social optimum's graph first, and when you close it the equilibrium graph shows. Uses `networkx` and `matplotlib`.

We compute the Traffic/Nash Equilibrium by using the path_cost function which calculates the cost of a driver going down a path. This is implemented in a nested for loop that continuously checks to see if the randomly assigned path is better than a newly created path. Once there are no changes, then it ends the for loop and sends a list of which path the drivers took. 


## Running the program
Note*** Our program runs correctly on Windows computers, but sometimes the math rounds strangely when using a Macbook.
Note*** We cannot submit an example file so just ignore mentions of it. 

When creating the `gml` file, please use the format given in our example file. Specifically, we need an `a` and a `b` value for each edge to calculate ax+b.

Example Command:
`python ./traffic_analysis.py traffic.gml 4 0 3 --plot`

`traffic.gml` is our input file. There are `4` drivers in our graph, starting at node `0` going to node 

Ommitting the `--plot` flag will still output analysis to the console without the visual aids.
