"""
Built-in commands for pysh.

Built-in commands are handled directly by the shell, rather than by
running an external program. For example, 'cd' must be a built-in
because changing directory needs to affect the shell process itself.

Each built-in is a function that takes a list of string arguments.
Look at builtin_pwd below as a complete example to follow.
"""

import os
import sys
import psutil


# ---------------------------------------------------------------------------
# Example built-in: pwd
# ---------------------------------------------------------------------------


def builtin_pwd(args):
    """
    Print the current working directory.

    Uses os.getcwd() which asks the operating system for the current
    working directory of this process.

    Example usage:
        pysh /home/student $ pwd
        /home/student
    """
    print(os.getcwd())


# ---------------------------------------------------------------------------
# Example built-in: exit
# ---------------------------------------------------------------------------


def builtin_exit(args):
    """
    Exit the shell.

    Raises SystemExit which is caught by the main loop in shell.py
    to break out of the loop cleanly.
    """
    sys.exit(0)


# ---------------------------------------------------------------------------
# TODO: Implement the remaining built-in commands below.
#       Each function receives a list of string arguments.
#       Look at builtin_pwd above as an example to follow.
# ---------------------------------------------------------------------------

def builtin_cd(args):
    os.chdir(args[0])

def builtin_echo(args):
    print(" ".join(args))

def builtin_help(args):
    print("  help - Show this help message")
    print("Available built-in commands:")
    print("  pwd - Print the current working directory")
    print("  exit - Exit the shell")
    print("  cd <dir> - Change the current directory to <dir>")
    print("  echo <args> - Print the arguments to the console")
    print("  procinfo <pid> - Show information about a process")
    print("  cat <file> - Print the contents of a file")
    print("  head <file> <n> - Print the first n lines of a file")

def builtin_procinfo(args):
    try:
        pid = int(args[0])
        process = psutil.Process(pid)

        status = process.status()
        memory = process.memory_info().rss
        cpu_times = process.cpu_times()
        cpu_time = cpu_times.user + cpu_times.system
        ppid = process.ppid()

        print(f"PID: {pid}")
        print(f"Status: {status}")
        print(f"Memory: {memory} bytes")
        print(f"CPU Time: {cpu_time:.3f}s")
        print(f"Parent PID: {ppid}")

    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} does not exist.")
    except Exception as e:
        print(f"Error retrieving process information: {e}")


def builtin_cat(args):
    filename = args[0]

    try:
        with open(filename, "r") as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print(f"cat: {filename}: No such file")
    except PermissionError:
        print(f"cat: {filename}: Permission denied")

def builtin_head(args):
    filename = args[0]
    rangeNum = args[1]
    content = []

    try:
        for i in range(int(rangeNum)):
            with open(filename, "r") as f:
                line = f.readline()
                content.append(line)
        print("\n".join(content))
    except FileNotFoundError:
        print(f"head: {filename}: No such file")
    except PermissionError:
        print(f"head: {filename}: Permission denied")

    
    
    
