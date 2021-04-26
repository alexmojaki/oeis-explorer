import itertools
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

import networkx

from parse import parse

parsed = parse()


def group_by_key_func(iterable, key_func):
    result = defaultdict(list)
    for item in iterable:
        result[key_func(item)].append(item)
    return result


def downloaded_graph():
    sequences = json.loads(Path("downloaded.json").read_text())

    graph = networkx.Graph()
    for anum, obj in sequences.items():
        graph.add_node(anum)
        for match in set(re.findall(r"A\d{6}\b", str(obj), re.IGNORECASE)):
            match = match.upper()
            if match != anum:
                graph.add_edge(anum, match)

    return graph


def find_special():
    by_term = defaultdict(set)
    for anum, seq in parsed.items():
        for term in seq.get("terms", []):
            if term > 10 ** 12 and len(set(str(term))) > 2:
                by_term[term].add(anum)

    return {term: group for term, group in by_term.items() if 5 <= len(group) <= 10}


def main():
    graph = downloaded_graph()
    components = list(map(frozenset, networkx.connected_components(graph)))
    components_by_anum = {anum: component for component in components for anum in component}

    good_groups = networkx.Graph()
    for group in find_special().values():
        by_component = group_by_key_func(group, lambda anum: components_by_anum[anum])
        if len(by_component) <= 1:
            continue

        good_groups.add_node(frozenset(group))

    for g1, g2 in itertools.combinations(good_groups, 2):
        if len(g1 & g2) >= 2:
            good_groups.add_edge(g1, g2)

    result = dict(groups=[])
    mentioned_anums = set()

    components = list(networkx.connected_components(good_groups))
    for group_component in components:
        group = frozenset.union(*group_component)
        if len(group) > 20:
            continue
        by_component = group_by_key_func(group, lambda anum: components_by_anum[anum])

        subgroups = []
        subgroup: list
        for subgroup in sorted(by_component.values(), key=len):
            paths = {
                anum: sorted(
                    [
                        networkx.shortest_path(graph, anum, other)
                        for other in subgroup
                        if other != anum
                    ],
                    key=len,
                )
                for anum in subgroup
            }
            mentioned_anums.update(subgroup, *itertools.chain.from_iterable(paths.values()))
            subgroups.append(
                [
                    dict(
                        anum=anum,
                        paths=[
                            dict(anum=path[-1], path=path[1:-1]) for path in paths[anum]
                        ],
                    )
                    for anum in sorted(
                        subgroup, key=lambda n: (sum(map(len, paths[n])), n)
                    )
                ]
            )

        counts = Counter(num for anum in group for num in set(parsed[anum]["terms"]))

        result["groups"].append(
            dict(
                group=sorted(group),
                subgroups=subgroups,
                common_terms=[
                    str(x)
                    for x in sorted(x for x, count in counts.items() if count > 1)
                ],
            )
        )
    result["sequences"] = {
        anum: dict(
            name=parsed[anum].get("name", "OEIS name missing"),
            terms=[str(x) for x in parsed[anum].get("terms", [])],
        )
        for anum in mentioned_anums
    }
    Path("frontend/src/result.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
