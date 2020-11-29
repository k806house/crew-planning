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


def compute_crew_pairings(raw_data):
    data = prepare_data(raw_data)
    duties = generate_duties(data)
    pairing_graph = construct_pairing_graph(duties, data)
    pairings = construct_pairings(pairing_graph, data)
    prob, status = optimize_crew_pairings(pairings, duties, data)
    unwrapped_pairings = []
    for p in filter(lambda x: x.varValue == 1, prob.variables()):
        p_idx = int(p.name.split('_')[1])
        unwrapped_pairings += [unwrap_pairing(pairings[p_idx], duties)]
    return unwrapped_pairings


def prepare_data(raw_data):
    rzd = raw_data
    # rzd['departure'] = pd.to_datetime(rzd['departure'],
    #                                   utc=True).dt.tz_convert(None)
    # rzd['arrival'] = pd.to_datetime(rzd['arrival'],
    #                                 utc=True).dt.tz_convert(None)
    # rzd = rzd.rename(columns={
    #     'train': 'activity',
    #     'from': 'source',
    #     'to': 'stock'
    # })
    # rzd['passenger'] = 0

    rzd = rzd.rename(columns={
        'train_id': 'activity',
        'date_start': 'departure',
        'date_end': 'arrival',
        'departure_id': 'source',
        'arrival_id': 'stock',
        'id': 'trip_id'
    })

    rzd['activity'] = rzd['activity'].apply(str)
    rzd['source'] = rzd['source'].apply(str)
    rzd['stock'] = rzd['stock'].apply(str)

    print(rzd['source'].unique())
    print(rzd['activity'].unique())
    print(rzd['stock'].unique())

    rzd['departure'] = pd.to_datetime(rzd['departure'])
                                    #   utc=True).dt.tz_convert(None)
    rzd['arrival'] = pd.to_datetime(rzd['arrival'])
                                    # utc=True).dt.tz_convert(None)
    rzd['passenger'] = 0

    data = rzd

    data['departure'] = pd.to_datetime(data['departure'], dayfirst=True)
    data['arrival'] = pd.to_datetime(data['arrival'], dayfirst=True)
    # data = data.loc[(data['departure'] < datetime.datetime.strptime('2020-12-08', '%Y-%m-%d')) &\
    #                 (data['departure'] > datetime.datetime.strptime('2020-12-01', '%Y-%m-%d')),
    #                 data.columns].reset_index(drop=True)
    data['trip_id'] = data.index

    data_passenger = data[data['passenger'] == 0].copy()
    data_passenger['trip_id'] += len(data)
    data_passenger['passenger'] = 1

    data.loc[data['passenger'] == 0, 'departure'] -= datetime.timedelta(
        hours=1.5)
    data.loc[data['passenger'] == 0, 'arrival'] += datetime.timedelta(
        minutes=47)
    # data.loc[data['passenger'] == 0, 'arrival'] += (data['arrival'] - data['departure']) / 2

    data = pd.concat([data, data_passenger])
    data = data.append(
        {
            'activity': 'ANCHOR',
            'departure': datetime.datetime(year=2040, month=1, day=1),
            'arrival': datetime.datetime(year=2040, month=1, day=1),
            'source': '1',
            'stock': '2',
            'passenger': 1
        },
        ignore_index=True)
    data = data.append(
        {
            'activity': 'ANCHOR',
            'departure': datetime.datetime(year=2040, month=1, day=1),
            'arrival': datetime.datetime(year=2040, month=1, day=1),
            'source': '2',
            'stock': '1',
            'passenger': 1
        },
        ignore_index=True)

    data = data.drop(
        data[data['source'] == 'Самара, аквапарк'].index).reset_index(
            drop=True)
    data = data.drop(
        data[data['source'] == 'Пенза'].index).reset_index(drop=True)
    data['trip_id'] = data.index

    return data


def legal(duty):
    return len(duty) == 1


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
            trip = data.iloc[node.name]
            condition = (data['source'] == trip['stock']) & (data['departure'] > trip['arrival']) &\
            ((data['departure'] - trip['arrival'] <= datetime.timedelta(hours=15)) | (data['activity'] == 'ANCHOR'))
            adjacent_flights = data[condition].index
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
            min_rest = (other_duty[-1]['arrival'] -
                        other_duty[-1]['departure']) / 2
            if other_duty[-1]['arrival'] + min_rest < duty[0]['departure'] \
            and (duty[0]['departure'] - other_duty[-1]['arrival'] <= datetime.timedelta(hours=15)\
            or duty[0]['activity'] == 'ANCHOR'):
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
            nx.all_simple_paths(pairing_graph,
                                source_node,
                                stock_node,
                                cutoff=3))
    return pairings


def duty_by_name(name, duties):
    return duties[int(name.split('_')[-1])]


def duty_cost(duty):
    return sum([trip['passenger'] for trip in duty]) * 100


def pairing_cost(pairing, duties):
    duty1 = duty_by_name(pairing[1], duties)
    duty2 = duty_by_name(pairing[2], duties)
    return (duty2[0]['departure'] -
            duty1[-1]['arrival']).total_seconds() / 60 / 60


def init_lp_coeffs(pairings, duties, data):
    c = np.zeros(len(pairings))
    b = np.zeros((len(pairings), len(data[data['passenger'] == 0])))
    for idx, p in enumerate(pairings):
        c[idx] += pairing_cost(p, duties)
        for d in p:
            if d.startswith('Duty'):
                duty = duty_by_name(d, duties)
                c[idx] += duty_cost(duty)
                for trip in duty:
                    if trip['passenger'] == 0:
                        b[idx, trip['trip_id']] = 1
    return c, b


def optimize_crew_pairings(pairings, duties, data):
    c, b = init_lp_coeffs(pairings, duties, data)
    prob = LpProblem("CP", LpMinimize)

    # x_i == 1 if pairing_i is selected and zero otherwise
    x = LpVariable.matrix("x", list(range(len(pairings))), cat=LpBinary)
    s = b.T @ x
    for trip_idx in range(b.shape[1]):
        prob += lpSum(s[trip_idx]) == 1

    prob += lpDot(x, c) + lpSum(s)

    status = prob.solve()
    return prob, status
