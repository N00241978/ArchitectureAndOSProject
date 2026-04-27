import time
import psutil
import threading
import queue
import requests
from urllib import parse as urlparse
import os
from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW

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
    candidate = os.path.join(folder, filename)

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

            filename = safe_filename_from_url(url)
            filepath = unique_filepath(downloads_dir, filename)

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


def start_download_workers(num_workers):
    global downloader_started, download_threads

    if downloader_started:
        return

    for _ in range(num_workers):
        t = threading.Thread(target=download_worker, daemon=True)
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
        start_download_workers(worker_count)
    else:
        if worker_count != len(download_threads):
            print(
                f"{YELLOW}download: workers already running ({len(download_threads)} active). Using existing pool.{RESET}"
            )

    os.makedirs(os.path.join(os.getcwd(), "downloads"), exist_ok=True)

    for url in urls:
        download_queue.put(url)

    print(f"{GREEN}Queued {len(urls)} download(s){RESET}")
    print(f"{BLUE}Workers running:{RESET} {len(download_threads)}")
    print(f"{BLUE}Use 'download --status' to check progress.{RESET}")
