from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


def builtin_help(args):
    print(f"{GREEN}  help - Show this help message")
    print("  Available built-in commands:")
    print("  pwd - Print the current working directory")
    print("  exit - Exit the shell")
    print("  cd <dir> - Change the current directory to <dir>")
    print("  echo <args> - Print the arguments to the console")
    print("  procinfo <pid> - Show information about a process")
    print("  cat <file> - Print the contents of a file")
    print(f"  head <file> <n> - Print the first n lines of a file{RESET}")
