def allowed_file(filename):
    return filename.endswith('.csv')


def format_pairings(pairings):
    p_json = []
    for p in pairings:
        cur = []
        for t in p:
            t = t.drop('trip_id')
            t = t.drop('passenger')
            t['departure'] = t['departure'].strftime('%d/%m/%Y %H:%M')
            t['arrival'] = t['arrival'].strftime('%d/%m/%Y %H:%M')
            cur += [t.to_dict()]
        p_json.append(cur)
    return p_json
