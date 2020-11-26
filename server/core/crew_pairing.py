import datetime
import io
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from anytree import Node, NodeMixin, RenderTree
from pulp import *


def unwrap_pairing(pairing, duties):
    res = []
    for d in pairing[1:-1]:
        res += duty_by_name(d, duties)
    return res


def compute_crew_pairings(file):
    data = prepare_data(file)
    duties = generate_duties(data)
    pairing_graph = construct_pairing_graph(duties, data)
    pairings = construct_pairings(pairing_graph, data)
    prob, status = optimize_crew_pairings(pairings, duties, data)
    unwrapped_pairings = []
    for p in filter(lambda x: x.varValue == 1, prob.variables()):
        p_idx = int(p.name.split('_')[1])
        unwrapped_pairings += [unwrap_pairing(pairings[p_idx], duties)]
    return unwrapped_pairings


def prepare_data(file):
    data = pd.read_csv(
        file,
        sep=',',
        header=None,
        names=['departure', 'source', 'activity', 'stock', 'arrival'])

    data['departure'] = pd.to_datetime(data['departure'], dayfirst=True)
    data['arrival'] = pd.to_datetime(data['arrival'], dayfirst=True)
    data['trip_id'] = data.index
    return data


def legal(duty):
    duty_len = duty[-1].arrival - duty[0].departure
    return duty_len.total_seconds() < 16 * 60 * 60


def generate_duties(data):
    """During the duty generation process, it is the aim to find all possible sequences
    of flights that can legally be operated by a crew member in one workday.
    The resulting sequences are called duties. To generate these duties,
    a search tree containing all flights is enumerated in a breadth-first manner.
    The first layer of the tree consists of all flights in the schedule.
    At the beginning of the process, a stack that contains all nodes that
    still need to be explored is created. This entire first layer of nodes
    is added to the stack. Then, an iterative process takes place that
    terminates when the stack is empty. This process includes getting
    the first element, consisting of a path in the search tree, off the
    stack, and generating a duty including check-in and check-out activities
    based on the path. If this duty is legal, it will be appended to the list
    of all legal duties. Additionally, all flights that can be used to further
    extend the duty will be added as nodes in the tree. These nodes will be
    children of the last node of the path popped in the first step of the process.
    The last step of the iterative process is to add the paths from the root to
    the newly created nodes to the stack of unexplored options. Whenever a duty
    is not legal, no child nodes will be created, resulting in the branch to
    be pruned and not expanded upon further."""
    unexplored = []
    duties = []
    t = Node(-1)
    # All flights in the schedule are the first layer of children
    for _, r in data.iterrows():
        trip_node = Node(r['trip_id'], parent=t)
        unexplored.append(trip_node)

    # Breadth-first search
    while unexplored:
        node = unexplored.pop(0)  #Pop the first element of the stack
        duty = [data.iloc[n.name] for n in node.path[1:]]
        if legal(duty):
            duties.append(duty)
            adjacent_flights = data[(data['source'] == data.iloc[node.name]['stock']) &\
             (data['departure'] > data.iloc[node.name]['arrival'])].index
            for a in adjacent_flights:
                new = Node(a, parent=node)
                unexplored.append(new)

    return duties


def construct_pairing_graph(duties, data):
    """To generate feasible pairings, both models use a directed acyclic graph consisting of source
    and sink nodes (bases), nodes representing taxi movements, and nodes representing the duties
    from the duty generation step. The presence of an edge between nodes indicates that the
    activities can be performed sequentially. This resulting graph has O(n) nodes and O(n2) edges.
    In the graph, a path between the source and sink nodes of the same base then
    gives a pairing. To later enforce a maximum pairing duration, the edges have
    a resource cost attribute, which indicates the time needed to perform the
    activities in a sequence. The edges also have a weight attribute.
    The weights are assigned based on the time that the crew is on duty,
    but is not operating a flight. In this way, a connection between two
    duties without a lot of excessive rest in between is preferred to a connection
    that contains a lot of idle time. In addition, the use of taxi’s
    is discouraged by penalizing the edge with additional weight.
    In this way, a pairing that does not contain any positioning activities,
    is preferred to the same pairing with additional taxi activities.
    The cumulative weight of the edges in a path from sink to source gives
    the cost of the pairing to be used in the objective function.
    The graph is constructed by first creating individual nodes for all duties,
    all sources and all sinks. Additionally, two taxi nodes are created
    for each base. One of these nodes indicates the possibility of a pairing
    starting with a taxi commute from the base, while the other indicates
    the possibility of ending a pairing with a taxi commute to the base.
    Similarly, two nodes per base are created representing the combination
    of a taxi plus overnight stay. Next, all edges are determined."""
    pairing_graph = nx.DiGraph()

    stock_to_duties = defaultdict(list)
    for idx, duty in enumerate(duties):
        duty_label = f'Duty_{idx}'
        pairing_graph.add_node(duty_label, node_type='duty')
        stock_to_duties[duty[-1]['stock'] + '_source'].append(duty_label)

    for source in data['source'].unique():
        pairing_graph.add_node(f'{source}_source', node_type='source')

    for idx, duty in enumerate(duties):
        duty_label = f'Duty_{idx}'
        duty_source = duty[0]['source'] + '_source'
        duty_stock = duty[-1]['stock'] + '_stock'

        for d in stock_to_duties[duty_source]:
            num = d.split('_')[-1]
            other_duty = duties[int(num)]
            if other_duty[-1]['arrival'] < duty[0]['departure']:
                pairing_graph.add_edge(d, duty_label)

        pairing_graph.add_edge(duty_source, duty_label)
        pairing_graph.add_edge(duty_label, duty_stock)

    for stock in data['stock'].unique():
        pairing_graph.add_node(f'{stock}_stock', node_type='stock')

    return pairing_graph


def construct_pairings(pairing_graph, data):
    pairings = []
    for source in data['source'].unique():
        source_node = source + '_source'
        stock_node = source + '_stock'
        pairings += list(
            nx.all_simple_paths(pairing_graph, source_node, stock_node))
    return pairings


def duty_by_name(name, duties):
    return duties[int(name.split('_')[-1])]


def duty_cost(duty):
    return len(duty)


def init_lp_coeffs(pairings, duties, data):
    c = np.zeros(len(pairings))
    b = np.zeros((len(pairings), len(data)))
    for idx, p in enumerate(pairings):
        for d in p:
            if d.startswith('Duty'):
                duty = duty_by_name(d, duties)
                c[idx] += duty_cost(duty)
                for trip in duty:
                    b[idx, trip['trip_id']] = 1
    return c, b


def optimize_crew_pairings(pairings, duties, data):
    c, b = init_lp_coeffs(pairings, duties, data)
    prob = LpProblem("CP", LpMinimize)

    # x_i == 1 if pairing_i is selected and zero otherwise
    x = LpVariable.matrix("x", list(range(len(pairings))), 0, 1, LpInteger)
    s = b.T @ x
    for trip_idx in range(b.shape[1]):
        prob += lpSum(s[trip_idx]) >= 1

    prob += lpDot(x, c) + lpSum(s)

    status = prob.solve()
    return prob, status
