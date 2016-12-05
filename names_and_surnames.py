POLIMORF_PATH = "resources\\polimorf-20161127.tab"

def get_names():
    names = {}
    with open(POLIMORF_PATH, "r", encoding="utf-8") as f:
        for line in f:
            splitted = line.lower().split()
            if len(splitted) > 3 and splitted[3] == "imię":
                if splitted[1] not in names:
                    names[splitted[1]] = {}
                names[splitted[1]][splitted[2]] = splitted[0]
    return names


def get_names_variants():
    names = {}
    with open(POLIMORF_PATH, "r", encoding="utf-8") as f:
        for line in f:
            splitted = line.lower().split()
            if len(splitted) > 3 and splitted[3] == "imię":
                if splitted[0] not in names:
                    names[splitted[0]] = set()
                names[splitted[0]] |= set([splitted[2]])
    return names


def get_surnames():
    surnames = {}
    with open(POLIMORF_PATH, "r", encoding="utf-8") as f:
        for line in f:
            splitted = line.lower().split()
            if len(splitted) > 3 and splitted[3] == "nazwisko":
                if splitted[1] not in surnames:
                    surnames[splitted[1]] = {}
                surnames[splitted[1]][splitted[2]] = splitted[0]
    return surnames


def get_surnames_variants():
    surnames = {}
    with open(POLIMORF_PATH, "r", encoding="utf-8") as f:
        for line in f:
            splitted = line.lower().split()
            if len(splitted) > 3 and splitted[3] == "nazwisko":
                if splitted[0] not in surnames:
                    surnames[splitted[0]] = set()
                surnames[splitted[0]] |= set([splitted[2]])
    return surnames


if __name__ == "__main__":
    print(len(get_surnames()))
