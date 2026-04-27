from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


def builtin_head(args):
    filename = args[0]
    rangeNum = int(args[1])
    content = []

    try:
        with open(filename, "r") as f:
            for i in range(rangeNum):
                line = f.readline()
                content.append(line)
        print("\n".join(content))
    except FileNotFoundError:
        print(f"{RED}head: {filename}: No such file{RESET}")
    except PermissionError:
        print(f"{RED}head: {filename}: Permission denied{RESET}")
