from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


def builtin_cat(args):
    filename = args[0]

    try:
        with open(filename, "r") as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print(f"{RED}cat: {filename}: No such file{RESET}")
    except PermissionError:
        print(f"{RED}cat: {filename}: Permission denied{RESET}")
