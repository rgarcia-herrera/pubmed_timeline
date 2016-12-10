import argparse
import pickle
import networkx as nx
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Plot a pickled graph.')
parser.add_argument('--pickle',
                    type=argparse.FileType('r'),
                    required=True,
                    help="path to pickled nx graph")
parser.add_argument('--svg',
                    type=argparse.FileType('w'),
                    required=True,
                    help="path to output svg")

args = parser.parse_args()

g = pickle.load(args.pickle)

#pos=nx.spring_layout(g)

nx.draw_circular(g, with_labels=True,
                 node_size=[n.get_weight() for n in g.nodes()],
                 node_color='lightgrey',
                 edge_color='lightgrey',
                 alpha=0.6,
                 labels={n:n.term for n in g.nodes()})




plt.savefig(args.svg, format='svg')
