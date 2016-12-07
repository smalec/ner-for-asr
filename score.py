import bisect


def true_positives(selected, relevant):
    sorted_relevant = sorted(list(sum(relevant, ())))
    hits = []
    for (start_time, end_time) in selected:
        start_bisect_index = bisect.bisect(sorted_relevant, start_time)
        end_bisect_index = bisect.bisect(sorted_relevant, end_time)
        if start_bisect_index % 2 and end_bisect_index - start_bisect_index < 2:
            intersection = min(end_time, sorted_relevant[start_bisect_index]) - start_time
            union = max(end_time, sorted_relevant[start_bisect_index]) - sorted_relevant[start_bisect_index - 1]
            if intersection / union > 1/3:
                hits.append((start_time, end_time))
        elif (not start_bisect_index % 2) and 0 < end_bisect_index - start_bisect_index < 3:
            intersection = min(end_time, sorted_relevant[start_bisect_index + 1]) - sorted_relevant[start_bisect_index]
            union = max(end_time, sorted_relevant[start_bisect_index + 1]) - start_time
            if intersection / union > 1 / 3:
                hits.append((start_time, end_time))
    return hits


def precision(selected, relevant):
    return len(true_positives(selected, relevant))/len(selected)


def recall(selected, relevant):
    return len(true_positives(selected, relevant))/len(relevant)


def f1(selected, relevant):
    p, r = precision(selected, relevant), recall(selected, relevant)
    return 2*p*r/(p+r)


if __name__ == "__main__":
    selected = [(1.1, 2.38), (4.6899999999999995, 5.119999999999999), (573.84, 574.8900000000001)]
    relevant = [(1.1, 2.25), (4.45, 5.63)]
    print(f1(selected, relevant))
