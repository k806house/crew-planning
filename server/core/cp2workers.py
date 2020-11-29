from collections import defaultdict


def can_do(worker, worker2trip):
    return True
    return len(worker2trip[worker]) < 2


def assign_work(pairings, base):
    events = []
    trip2trip = {}
    for p in pairings:
        if p[1]['activity'] == 'ANCHOR':
            continue
        events.append((p[0]['departure'], p[0]))
        events.append((p[0]['arrival'], p[0]))
        events.append((p[1]['departure'], p[1]))
        events.append((p[1]['arrival'], p[1]))
        trip2trip[p[0]['trip_id']] = p[1]
        trip2trip[p[1]['trip_id']] = p[0]

    events = sorted(events)

    base_cnt = 0
    base_cur = []
    trip2worker = defaultdict(list)
    worker2trip = defaultdict(list)
    for ev in events:
        if ev[0] == ev[1]['departure']:
            if ev[1]['source'] == base:
                ok = False
                for idx, w in enumerate(base_cur):
                    if can_do(w, worker2trip):
                        worker2trip[w].append(ev[1])
                        trip2worker[ev[1]['trip_id']].append(w)
                        base_cur.pop(idx)
                        ok = True
                        break
                if not ok:
                    worker2trip[base_cnt].append(ev[1])
                    trip2worker[ev[1]['trip_id']].append(base_cnt)
                    base_cnt += 1
        else:
            if ev[1]['stock'] == base:
                trip_before = trip2trip[ev[1]['trip_id']]
                ws = trip2worker[trip_before['trip_id']]
                w = ws.pop(0)
                worker2trip[w].append(ev[1])
                base_cur.append(w)

    return worker2trip


def cp2workers(unwrapped_pairings):
    base1 = '1'
    base2 = '2'

    base1_schedule = assign_work(
        list(filter(lambda p: p[0]['source'] == base1, unwrapped_pairings)),
        base1)

    base2_schedule = assign_work(
        list(filter(lambda p: p[0]['source'] == base2, unwrapped_pairings)),
        base2)

    return base1_schedule, base2_schedule
