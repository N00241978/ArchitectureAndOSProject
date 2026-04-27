import psutil


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
