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
import time
import psutil
import threading
import queue
import requests

from urllib.parse import urlparse
from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


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
    print(f"{GREEN}  help - Show this help message")
    print("  Available built-in commands:")
    print("  pwd - Print the current working directory")
    print("  exit - Exit the shell")
    print("  cd <dir> - Change the current directory to <dir>")
    print("  echo <args> - Print the arguments to the console")
    print("  procinfo <pid> - Show information about a process")
    print("  cat <file> - Print the contents of a file")
    print(f"  head <file> <n> - Print the first n lines of a file{RESET}")

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
        print(f"{RED}cat: {filename}: No such file{RESET}")
    except PermissionError:
        print(f"{RED}cat: {filename}: Permission denied{RESET}")

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

def bytes_to_mb(num_bytes):
    return num_bytes / (1024 * 1024)

def clear_screen():
    os.system("clear")

def builtin_sysinfo(args):
    sort_by = "memory"
    interval = 2

    i = 0
    while i < len(args):
        if args[i] == "--sort":
            if i + 1 >= len(args):
                print(f"{RED}Error: --sort requires an argument{RESET}")
                return
            sort_by = args[i + 1].lower()
            if sort_by not in ("cpu", "memory"):
                print(f"{RED}Error: --sort argument must be 'cpu' or 'memory'{RESET}")
                return
            i += 2
        elif args[i] == "--interval":
            if i + 1 >= len(args):
                print(f"{RED}Error: --interval requires an argument{RESET}")
                return
            try:
                interval = float(args[i + 1])
                if interval <= 0:
                    print(f"{RED}Error: --interval must be a positive number{RESET}")
                    return
            except ValueError:
                print(f"{RED}Error: --interval must be a number{RESET}")
                return
            i += 2
        else:
            print(f"{RED}Error: Unknown argument {args[i]}{RESET}")
            return

    try:
        psutil.cpu_percent(interval=None)
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        while True:
            clear_screen()

            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()

            overall_cpu = psutil.cpu_percent(interval=None)
            per_core_cpu = psutil.cpu_percent(interval=None, percpu=True)

            processes = []
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                try:
                    info = proc.info
                    pid = info["pid"]
                    name = info["name"] or "Unknown"
                    memory_mb = bytes_to_mb(info["memory_info"].rss) if info["memory_info"] else 0
                    cpu_percent = proc.cpu_percent(interval=None)

                    processes.append({
                        "pid": pid,
                        "name": name,
                        "memory_mb": memory_mb,
                        "cpu_percent": cpu_percent
                    })

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            if sort_by == "cpu":
                processes.sort(key=lambda p: p["cpu_percent"], reverse=True)
            else:
                processes.sort(key=lambda p: p["memory_mb"], reverse=True)

            top_processes = processes[:10]

            print("=== SYSINFO ===")
            print()

            print(f"{GREEN}Memory Usage:{RESET}")
            print(f"  Total:      {bytes_to_mb(virtual_mem.total):.2f} MB")
            print(f"  Used:       {bytes_to_mb(virtual_mem.used):.2f} MB")
            print(f"  Available:  {bytes_to_mb(virtual_mem.available):.2f} MB")
            print(f"  Percent:    {virtual_mem.percent:.1f}%")
            print()

            print(f"{RED}Swap Usage:{RESET}")
            print(f"  Total:      {bytes_to_mb(swap_mem.total):.2f} MB")
            print(f"  Used:       {bytes_to_mb(swap_mem.used):.2f} MB")
            print(f"  Free:       {bytes_to_mb(swap_mem.free):.2f} MB")
            print(f"  Percent:    {swap_mem.percent:.1f}%")
            print()

            print(f"{YELLOW}CPU Usage:{RESET}")
            print(f"  Overall:    {overall_cpu:.1f}%")
            for index, core in enumerate(per_core_cpu):
                print(f"  Core {index}:    {core:.1f}%")
            print()

            print(f"{BLUE}Top 10 Processes (sorted by {sort_by}):{RESET}")
            print(f"{'PID':>6} {'NAME':<25} {'CPU %':>8} {'MEM MB':>10}")
            print("-" * 55)

            for proc in top_processes:
                print(f"{proc['pid']:>6} {proc['name'][:25]:<25} {proc['cpu_percent']:>8.1f} {proc['memory_mb']:>10.2f}")

            print()
            print(f"{BLUE}Refreshing every {interval} second(s). Press Ctrl+C to return to shell.{RESET}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print()
        print(f"{RED}Exiting sysinfo...{RESET}")

download_queue = queue.Queue()
download_lock = threading.Lock()
completed_downloads = 0
active_workers = 0
download_threads = []
downloader_started = False

def safe_filename_from_url(url):
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)

    if not name:
        name = "downloaded_file"

    return name

def unique_filepath(folder, filename):
    base, ext = os.path.splitext(filename)
    counter = 1

    while os.path.exists(candidate):
        candidate = os.path.join(folder, f"{base}_{counter}{ext}")
        counter += 1

    return candidate

def download_worker():
    global completed_downloads, active_workers

    while True:
        url = download_queue.get()

        with download_lock:
            active_workers += 1
        
        try:
            downloads_dir = os.path.join(os.getcwd(), "downloads")
            os.makedirs(downloads_dir, exist_ok=True)

            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()

            filename = _safe_filename_from_url(url)
            filepath = _unique_filepath(downloads_dir, filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            with download_lock:
                completed_downloads += 1

            print(f"{GREEN}Downloaded:{RESET} {url} -> {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"{RED}download error:{RESET} {url} ({e})")
        except Exception as e:
            print(f"{RED}file error:{RESET} {url} ({e})")
        finally:
            with download_lock:
                active_workers -= 1
            download_queue.task_done()


def _start_download_workers(num_workers):
    global downloader_started, download_threads

    if downloader_started:
        return

    for _ in range(num_workers):
        t = threading.Thread(target=_download_worker, daemon=True)
        t.start()
        download_threads.append(t)

    downloader_started = True

def builtin_download(args):
    global downloader_started

    if not args:
        print(f"{RED}Usage:{RESET} download <file> [-w number] | download --status")
        return

    if args[0] == "--status":
        with download_lock:
            queued = download_queue.qsize()
            active = active_workers
            completed = completed_downloads
            workers = len(download_threads)

        print(f"{BLUE}Download Status{RESET}")
        print(f"  Queued:     {queued}")
        print(f"  Active:     {active}")
        print(f"  Completed:  {completed}")
        print(f"  Workers:    {workers}")
        return

    url_file = args[0]
    worker_count = 3

    if len(args) > 1:
        if len(args) == 3 and args[1] == "-w":
            try:
                worker_count = int(args[2])
                if worker_count <= 0:
                    print(f"{RED}download: worker count must be greater than 0{RESET}")
                    return
            except ValueError:
                print(f"{RED}download: invalid worker count{RESET}")
                return
        else:
            print(f"{RED}Usage:{RESET} download <file> [-w number] | download --status")
            return

    try:
        with open(url_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{RED}download: {url_file}: No such file{RESET}")
        return
    except PermissionError:
        print(f"{RED}download: {url_file}: Permission denied{RESET}")
        return

    if not urls:
        print(f"{YELLOW}download: no URLs found in {url_file}{RESET}")
        return

    if not downloader_started:
        _start_download_workers(worker_count)
    else:
        if worker_count != len(download_threads):
            print(f"{YELLOW}download: workers already running ({len(download_threads)} active). Using existing pool.{RESET}")

    os.makedirs(os.path.join(os.getcwd(), "downloads"), exist_ok=True)

    for url in urls:
        download_queue.put(url)

    print(f"{GREEN}Queued {len(urls)} download(s){RESET}")
    print(f"{BLUE}Workers running:{RESET} {len(download_threads)}")
    print(f"{BLUE}Use 'download --status' to check progress.{RESET}")