import os
import requests
import queue
import threading
from urllib import parse as urlparse
from pysh.colors import BLUE, GREEN, RESET, RED, YELLOW


download_state = {
    "queue": queue.Queue(),
    "threads": [],
    "active": [],
    "completed": [],
    "failed": [],
    "download_dir": "downloads",
    "lock": threading.Lock(),
}


def download_worker() -> None:
    while True:
        url = download_state["queue"].get()

        with download_state["lock"]:
            download_state["active"].append(url)

        try:
            os.makedirs(download_state["download_dir"], exist_ok=True)

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            parsed = urlparse.urlparse(url)
            filename = os.path.basename(parsed.path) or "downloaded_file"
            filepath = os.path.join(download_state["download_dir"], filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            with download_state["lock"]:
                download_state["completed"].append(url)

            # print(f"{GREEN}Downloaded:{RESET} {url} -> {filepath}")

        except requests.exceptions.RequestException as e:
            with download_state["lock"]:
                download_state["failed"].append((url, e))

            print(f"{RED}download error:{RESET} {url} ({e})")

        except Exception as e:
            with download_state["lock"]:
                download_state["failed"].append((url, e))

            print(f"{RED}file error:{RESET} {url} ({e})")

        finally:
            with download_state["lock"]:
                if url in download_state["active"]:
                    download_state["active"].remove(url)

            download_state["queue"].task_done()


def builtin_download(args) -> None:
    if not args:
        print(f"{RED}Usage:{RESET} download <file> [-w number] | download --status")
        return

    if args[0] == "--status":
        with download_state["lock"]:
            queued = download_state["queue"].qsize()
            workers = len(download_state["threads"])
            active = len(download_state["active"])
            completed = len(download_state["completed"])
            failed = len(download_state["failed"])

        print(f"{BLUE}Download Status{RESET}")
        print(f"  Queued:     {queued}")
        print(f"  Workers:    {workers}")
        print(f"  Active:     {active}")
        print(f"  Completed:  {completed}")
        print(f"  Failed:     {failed}")
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

    os.makedirs(download_state["download_dir"], exist_ok=True)

    while len(download_state["threads"]) < worker_count:
        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()
        download_state["threads"].append(thread)

    for url in urls:
        download_state["queue"].put(url)

    print(f"{GREEN}Queued {len(urls)} download(s){RESET}")
    print(f"{BLUE}Workers running:{RESET} {len(download_state['threads'])}")
    print(f"{BLUE}Use 'download --status' to check progress.{RESET}")
