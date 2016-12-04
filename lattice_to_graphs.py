import os
from collections import Counter


def get_sources(graph):
    return graph['nodes'].keys() - { edge["to"] for edge in graph['edges'] }


def get_sinks(graph):
    return graph['nodes'].keys() - { edge["from"] for edge in graph['edges'] }


def get_offsets(sil_split_directory):
    files = [os.path.join(sil_split_directory, f)
             for f in os.listdir(sil_split_directory) if os.path.isfile(os.path.join(sil_split_directory, f))]
    offsets = []
    for file in sorted(files):
        with open(file, "r", encoding="utf-8") as f:
            offsets.append([])
            offset_expexted = False
            for part in f.read().split("|"):
                if offset_expexted:
                    offsets[-1].append(float(part))
                    offset_expexted = False
                else:
                    if part == "":
                        offset_expexted = True
    return offsets


def get_fresh_id(graph):
    nodes = graph['nodes']
    for x in range(0, 1+len(nodes)):
        if str(x) not in nodes:
            return str(x)


def get_outgoing_edges(graph):
    outgoing_edges = {}
    for edge in graph['edges']:
        from_id = edge['from']
        if from_id not in outgoing_edges:
            outgoing_edges[from_id] = []
        outgoing_edges[from_id].append(edge)
    return outgoing_edges


def get_topological_order(graph):
    edges = graph['edges']
    nodes = graph['nodes']
    outgoing_edges = get_outgoing_edges(graph)

    dependencies_count = Counter(edge["to"] for edge in edges)

    ready_ids = [id for id in nodes if not dependencies_count[id]]

    ordered_ids = []
    while ready_ids:
        id = ready_ids.pop()
        ordered_ids.append(id)
        for edge in outgoing_edges.get(id, []):
            to_id = edge["to"]
            dependencies_count[to_id] -= 1
            if dependencies_count[to_id] == 0:
                ready_ids.append(to_id)
    return ordered_ids


def add_timestamps(graph, offset):
    nodes = graph['nodes']
    outgoing_edges = get_outgoing_edges(graph)
    for id in get_topological_order(graph):
        node = nodes[id]
        if "timestamp" not in node:
            node["timestamp"] = offset
        for edge in outgoing_edges.get(id, []):
            timestamp = edge["duration"] + node["timestamp"]
            to_id = edge["to"]
            to = nodes[to_id]
            to["timestamp"] = max(timestamp, to.get("timestamp", 0))
    return graph


def concatenate_graphs(graphs):
    def epsilon_edge(from_id, to_id):
        return {
            "from": from_id,
            "to": to_id,
            "text": "<eps>",
            "graph_cost": 0.0,
            "acoustic_cost": 0.0,
            "duration": 0.0,
        }
    todo = []
    for graph in graphs:
        nodes = graph["nodes"]
        edges = graph["edges"]

        def ensure_single_end(get_ends, combine_times, insert_before):
            ends = get_ends(graph)
            if len(ends) == 1:
                return ends.pop()

            end = get_fresh_id(graph)
            nodes[end] = {
                "is_on_best_path": True,
                "timestamp": combine_times([nodes[id]["timestamp"] for id in ends]),
            }
            for id in ends:
                edges.append(epsilon_edge(end, id) if insert_before else epsilon_edge(id, end))
            return end

        source = ensure_single_end(get_sources, min, True)
        sink = ensure_single_end(get_sinks, max, False)
        todo.append((nodes[source]["timestamp"], nodes, edges, source, sink))

    output_nodes = {}
    output_edges = []
    last_sink = None
    free_id = 0
    for start, nodes, edges, source, sink in todo:
        local_id_to_global_id = {}
        for id in sorted(nodes.keys()):
            local_id_to_global_id[id] = str(free_id)
            output_nodes[local_id_to_global_id[id]] = nodes[id]
            free_id += 1
        for edge in edges:
            for side in ["from", "to"]:
                edge[side] = local_id_to_global_id[edge[side]]
            output_edges.append(edge)
        if last_sink:
            output_edges.append(epsilon_edge(last_sink, local_id_to_global_id[source]))
        last_sink = local_id_to_global_id[sink]

    return {"nodes": output_nodes, "edges": output_edges}


def lattice_to_graphs(lattice_path, sil_split_dir):
    utterance_id = None
    lattices = {}
    with open(lattice_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                words = line.split()
                if utterance_id is None:
                    utterance_id = words[0][-7:-4]
                    edges = []
                elif len(words) == 4:
                    (from_id, to_id, text, weight) = words
                    (graph_cost, acoustic_cost, transitions_ids) = weight.split(',')
                    edges.append({
                        "from": from_id,
                        "to": to_id,
                        "text": text,
                        "graph_cost": float(graph_cost),
                        "acoustic_cost": float(acoustic_cost),
                        "duration": sum([1 for _ in transitions_ids.split('_')])/100,
                    })
            else:
                nodes = {}
                for edge in edges:
                    for id in [edge["from"], edge["to"]]:
                        nodes[id] = {}
                graph = {
                    "nodes": nodes,
                    "edges": edges,
                }
                if utterance_id not in lattices:
                    lattices[utterance_id] = []
                lattices[utterance_id].append(graph)
                utterance_id = None
    offsets = get_offsets(sil_split_dir)
    for i, utt in enumerate(sorted(lattices.keys())):
        for j, line_graph in enumerate(lattices[utt]):
            add_timestamps(line_graph, offsets[i][j])
    return {utt_id: concatenate_graphs(graphs) for utt_id, graphs in lattices.items()}


if __name__ == "__main__":
    graphs = lattice_to_graphs("D:\\ext.txt", "D:\\sil_split")
    print(graphs["000"])
