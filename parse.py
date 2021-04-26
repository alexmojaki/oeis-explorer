from collections import defaultdict


def raw_lines(filename):
    with open(filename) as f:
        result = f.readlines()

    for i, line in enumerate(result):
        if not line.startswith("#"):
            assert line.startswith("A000001 ")
            return result[i:]


def parse():
    result = defaultdict(dict)

    for line in raw_lines("stripped"):
        anum, seq = line.split(" ,")
        result[anum]["terms"] = tuple(map(int, seq.rstrip("\n,").split(",")))

    for line in raw_lines("names"):
        anum, name = line.split(" ", 1)
        result[anum]["name"] = name

    return result


if __name__ == "__main__":
    print(len(parse()))
