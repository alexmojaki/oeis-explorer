from collections import defaultdict


def raw_lines(filename):
    try:
        with open(filename) as f:
            result = f.readlines()

        for i, line in enumerate(result):
            if not line.startswith("#"):
                assert line.startswith("A000001 ")
                return result[i:]
    except Exception as e:
        raise ValueError(
            "Download and extract the files https://oeis.org/stripped.gz and https://oeis.org/names.gz. "
            "The resulting files should be called `names` and `stripped`, no extensions."
        ) from e


def parse():
    """
    Returns a dictionary {anum: {terms: [ints], name: "string"}}
    parsed from the raw files on the OEIS site.
    """
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
