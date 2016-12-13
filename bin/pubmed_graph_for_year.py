from pubmed_timeline import Term
from pubmed_timeline import Citation
from Bio import Medline
import networkx as nx
import itertools
import operator
import json
import argparse
import sys
import pickle

parser = argparse.ArgumentParser(description='Create timeline of keyword "volumes" in CSV file.')
parser.add_argument('--medline',
                    type=argparse.FileType('r'),
		    default=sys.stdin,
                    help="citations file in medline format")
parser.add_argument('--start_year',
                    type=int,
                    required=True,
                    help="start year of timeline")
parser.add_argument('--thru_year',
                    type=int,
                    required=True,
                    help="end year of timeline")
parser.add_argument('--mode',
                    choices=['flatmesh',
                             'meshterms',
                             'keywords',
                             'kw+mh',
                             'kw+flatmh'],
                    default='both',
                    help="extract mesh-terms, keywords or both")
parser.add_argument('--groups',
                    type=argparse.FileType('r'),
                    required=False,
                    help="dictionary that groups similar terms, in json format")
parser.add_argument('--ignore',
                    type=argparse.FileType('r'),
                    required=False,
                    help="file with list of terms to remove from network")
parser.add_argument('--top',
                     type=int,
                     default=0,
                     help="how many top terms")
parser.add_argument('--pickle',
                    type=argparse.FileType('w'),
                    required=True,
                    help="path to output pickled nx graph")

args = parser.parse_args()

if args.groups:
    group_terms = json.load(args.groups)
else:
    group_terms = {}
    
records = Medline.parse(args.medline)

G = nx.Graph()

for r in records:
    c = Citation(r)

    if c.date.year not in range(args.start_year, args.thru_year):
        continue
    
    if args.mode == 'meshterms':
        local_terms = c.get_meshterms(flatten=False, groups=group_terms)
    elif args.mode == 'flatmesh':
        local_terms = c.get_meshterms(flatten=True, groups=group_terms)        
    elif args.mode == 'keywords':
        local_terms = c.get_keywords(groups=group_terms)
    elif args.mode == 'kw+mh':
        local_terms = c.get_keywords(groups=group_terms) + c.get_meshterms(flatten=False, groups=group_terms)
    elif args.mode == 'kw+flatmh':
        local_terms = c.get_keywords(groups=group_terms) + c.get_meshterms(flatten=True, groups=group_terms)

    for term in local_terms:
        if term in G:
            w = G.node[term]['w'] + 1
            years = G.node[term]['years']
            years[c.date.year] += 1
            G.add_node(term, w=w, years=years)
        else:
            years = {y:0 for y in range(args.start_year, args.thru_year+1)}
            years[c.date.year] += 1
            G.add_node(term, w=1, years=years)
        
    for pair in itertools.combinations(local_terms, 2):
        n0 = pair[0]
        n1 = pair[1]
        
        w = G.get_edge_data(n0, n1, default={'w':0})['w'] + 1
        G.add_edge(n0, n1, {'w': w})


# remove uninteresting terms
if args.ignore:
    for t in args.ignore.readlines():
        term = t.strip()
        if term in G:
            G.remove_node(term)

degree_sorted = sorted(G.degree(weight='w').items(), key=operator.itemgetter(1))

degree_sorted.reverse()

if args.top == 0:
    top = [t[0] for t in degree_sorted]
else:
    top = [t[0] for t in degree_sorted[:args.top]]

delete = set(G.nodes()) - set(top)

G.remove_nodes_from(delete)

pickle.dump(G, args.pickle)
