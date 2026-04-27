from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW
import os
import psutil
import time


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
            except psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess:
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
                    memory_mb = (
                        bytes_to_mb(info["memory_info"].rss)
                        if info["memory_info"]
                        else 0
                    )
                    cpu_percent = proc.cpu_percent(interval=None)

                    processes.append(
                        {
                            "pid": pid,
                            "name": name,
                            "memory_mb": memory_mb,
                            "cpu_percent": cpu_percent,
                        }
                    )

                except psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess:
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
                print(
                    f"{proc['pid']:>6} {proc['name'][:25]:<25} {proc['cpu_percent']:>8.1f} {proc['memory_mb']:>10.2f}"
                )

            print()
            print(
                f"{BLUE}Refreshing every {interval} second(s). Press Ctrl+C to return to shell.{RESET}"
            )

            time.sleep(interval)

    except KeyboardInterrupt:
        print()
        print(f"{RED}Exiting sysinfo...{RESET}")
