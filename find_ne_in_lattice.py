from lattice_to_graphs import get_outgoing_edges, lattice_to_graphs
from names_and_surnames import get_names, get_names_variants, get_surnames, get_surnames_variants


def find_phrase(phrase, graph):
    tokens = phrase.lower().split()
    results = {}
    edges = graph["edges"]
    nodes = graph["nodes"]
    outgoing_edges = get_outgoing_edges(graph)
    for edge in edges:
        if edge["text"] == tokens[0]:
            start_node, end_node = edge["from"], edge["to"]
            found = True
            for token in tokens[1:]:
                found_next_token = False
                for next_edge in outgoing_edges.get(end_node, []):
                    if token == next_edge["text"]:
                        found_next_token = True
                        end_node = next_edge["to"]
                if not found_next_token:
                    found = False
                    break
            if found:
                results[(nodes[start_node]["timestamp"], nodes[end_node]["timestamp"])] = phrase
    return results


def find_person(names, surnames, graph):
    base = get_names()
    base.update(get_surnames())
    names = names.lower().split() + surnames.lower().split()
    tagset = base[names[0]].keys()
    for name in names[1:]:
        tagset &= base[name].keys()
    results = {}
    for tag in tagset:
        phrase = " ".join([base[name][tag] for name in names])
        results.update(find_phrase(phrase, graph))
    return results


def find_all_persons(graph):
    names = get_names_variants()
    surnames = get_surnames_variants()
    results = {}
    edges = graph["edges"]
    nodes = graph["nodes"]
    outgoing_edges = get_outgoing_edges(graph)
    for edge in edges:
        if edge["text"] in names:
            for next_edge in outgoing_edges[edge["to"]]:
                if next_edge["text"] in surnames and names[edge["text"]] & surnames[next_edge["text"]] != set():
                    timestamps = (nodes[edge["from"]]["timestamp"], nodes[next_edge["to"]]["timestamp"])
                    results[timestamps] = " ".join([edge["text"], next_edge["text"]])
    return merge_base_on_timestamps(results)


def merge_base_on_timestamps(results):
    sorted_results = sorted(list(results.keys()))
    merged = [list(sorted_results[0])]
    for (start_time, end_time) in sorted_results[1:]:
        if start_time < merged[-1][1] and merged[-1][1] - start_time >= (end_time - start_time)/2:
            merged[-1][1] = end_time
        else:
            merged.append([start_time, end_time])
    return [(timestamp[0], timestamp[1]) for timestamp in merged]


if __name__ == "__main__":
    graphs = lattice_to_graphs("D:\\extracted_lattice.txt", "D:\\sil_split")
    print(find_all_persons(graphs["000"]))
