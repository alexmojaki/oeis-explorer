import itertools
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

import networkx

from parse import parse


def supplemented_parsed():
    result = parse()
    for anum, data in list(result.items()):
        for factor in [2, 3]:
            result[f"{anum} * {factor}"] = dict(
                name=data.get("name", "OEIS name missing"),
                terms=[x * factor for x in data.get("terms", [])],
            )
        for add in [1, 2, 3]:
            result[f"{anum} + {add}"] = dict(
                name=data.get("name", "OEIS name missing"),
                terms=[x + add for x in data.get("terms", [])],
            )
    return result


parsed = supplemented_parsed()


def group_by_key_func(iterable, key_func):
    """
    Create a dictionary from an iterable such that the keys are the result of evaluating a key function on elements
    of the iterable and the values are lists of elements all of which correspond to the key.

    >>> def si(d): return sorted(d.items())
    >>> si(group_by_key_func("a bb ccc d ee fff".split(), len))
    [(1, ['a', 'd']), (2, ['bb', 'ee']), (3, ['ccc', 'fff'])]
    >>> si(group_by_key_func([-1, 0, 1, 3, 6, 8, 9, 2], lambda x: x % 2))
    [(0, [0, 6, 8, 2]), (1, [-1, 1, 3, 9])]
    """
    result = defaultdict(list)
    for item in iterable:
        result[key_func(item)].append(item)
    return result


def oeis_graph():
    """
    Returns a graph where the nodes are sequences and an edge
    indicates that at least one of the pages of two sequences
    mentions the A-number of the other sequence somewhere.

    The graph is based on the file full_sequences.json which
    should be downloaded separately from
    https://drive.google.com/file/d/1bN3LrTGRenfw-esiBe4GI0CqtIfPWjlC/view?usp=sharing
    This contains about 100k sequences, not the full OEIS.
    It may be significantly out of date when you run this code.
    """
    try:
        sequences = json.loads(Path("full_sequences.json").read_text())
    except Exception as e:
        raise ValueError(
            "Download the file full_sequences.json from "
            "https://drive.google.com/file/d/1bN3LrTGRenfw-esiBe4GI0CqtIfPWjlC/view?usp=sharing"
        ) from e

    graph = networkx.Graph()
    for anum, obj in sequences.items():
        graph.add_node(anum)
        for match in set(re.findall(r"A\d{6}\b", str(obj), re.IGNORECASE)):
            match = match.upper()
            if match != anum:
                graph.add_edge(anum, match)

    return graph


def find_special():
    """
    Returns a dictionary {term: group} where:

    - `term` is a number greater than a trillion with more than two distinct digits
    - `group` is a list of 5 to 10 sequences (A-number strings)
    - `term` is found in every sequence in `group`

    The idea is that groups which are too small are more likely to be coincidences or
    lacking in useful information for a viewer, while groups that are too big
    tend to contain generic sequences like "powers of 2" where matching terms are
    unsurprising and users are overloaded with information.
    """
    by_term = defaultdict(set)
    for anum, seq in parsed.items():
        for term in seq.get("terms", []):
            if term > 10 ** 12 and len(set(str(term))) > 2:
                by_term[term].add(anum)

    return {
        term: group
        for term, group in by_term.items()
        if 5 <= len(group) <= 10 and len(set(anum[-3:] for anum in group)) > 1
    }


def main():
    graph = oeis_graph()
    components = list(map(frozenset, networkx.connected_components(graph)))
    components_by_anum = {anum: component for component in components for anum in component}

    good_groups = networkx.Graph()
    for group in find_special().values():
        by_component = group_by_key_func(
            group, lambda anum: components_by_anum[anum.split()[0]]
        )
        # Only consider groups with multiple subgroups, otherwise the relationship
        # between all the sequences is already known.
        if len(by_component) <= 1:
            continue

        good_groups.add_node(frozenset(group))

    # find_special is the starting point for creating groups, where one term
    # is found in every sequence. But this leads to groups which are very similar but
    # not identical. We merge groups together if they share at least two terms.
    for g1, g2 in itertools.combinations(good_groups, 2):
        if len(g1 & g2) >= 2:
            good_groups.add_edge(g1, g2)

    result = dict(groups=[])
    mentioned_anums = set()

    components = list(networkx.connected_components(good_groups))
    for i, group_component in enumerate(components):
        print(f"On component {i + 1} of {len(components)}")
        # This is the result of one or more simple groups from find_special merged together
        # This means there might not be any terms that are found in all sequences in the group.
        # Again, we avoid massive groups that are probably overwhelming or not that interesting
        group = frozenset.union(*group_component)
        if len(group) > 20:
            continue

        # This is components in the oeis_graph, i.e. edges based on links/mentions, not terms
        by_component = group_by_key_func(
            group, lambda anum: components_by_anum[anum.split()[0]]
        )

        subgroups = []
        subgroup: list
        for subgroup in sorted(by_component.values(), key=len):
            clean_subgroup = [anum.split()[0] for anum in subgroup]
            paths = {
                anum: sorted(
                    [
                        networkx.shortest_path(graph, anum, other)
                        for other in clean_subgroup
                        if other != anum
                    ],
                    key=len,
                )
                for anum in clean_subgroup
            }
            mentioned_anums.update(
                subgroup,
                *[graph[anum] for anum in clean_subgroup],
                *itertools.chain.from_iterable(paths.values()),
            )
            subgroups.append(
                dict(
                    nodes=[
                        dict(
                            anum=anum,
                            paths=[
                                dict(anum=path[-1], path=path[1:-1])
                                for path in paths[anum.split()[0]]
                            ],
                            neighbours=sorted(graph[anum.split()[0]]),
                        )
                        for anum in sorted(
                            subgroup,
                            key=lambda n: (sum(map(len, paths[n.split()[0]])), n),
                        )
                    ],
                    # Too expensive!
                    # on_shortest_paths=sorted(
                    #     set(
                    #         itertools.chain.from_iterable(
                    #             itertools.chain.from_iterable(
                    #                 networkx.all_shortest_paths(graph, u, v)
                    #                 for u, v in itertools.combinations(subgroup, 2)
                    #             )
                    #         )
                    #     )
                    #     - set(subgroup)
                    # ),
                )
            )

        counts = Counter(num for anum in group for num in set(parsed[anum]["terms"]))

        result["groups"].append(
            dict(
                group=sorted(group),
                subgroups=subgroups,
                common_terms=[
                    str(x)  # so javascript can read the full number from JSON
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
