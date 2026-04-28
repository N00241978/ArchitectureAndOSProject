from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


def builtin_echo(args):
    print(f"{YELLOW} ".join(f"{YELLOW}{arg}{RESET}" for arg in args))
