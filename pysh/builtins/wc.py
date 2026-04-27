from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


def builtin_wc(args):
    filename = args[0]

    try:
        with open(filename, "r") as f:
            lines = 0
            words = 0
            chars = 0

            for line in f:
                lines += 1
                words += len(line.split())
                chars += len(line)

        print(f"{lines} {words} {chars} {filename}")

    except FileNotFoundError:
        print(f"{RED}wc: {filename}: No such file{RESET}")
    except PermissionError:
        print(f"{RED}wc: {filename}: Permission denied{RESET}")
