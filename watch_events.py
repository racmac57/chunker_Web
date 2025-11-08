from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import multiprocessing as mp


def file_is_settled(p: Path, seconds: int = 2) -> bool:
    try:
        s1, t1 = p.stat().st_size, p.stat().st_mtime
        time.sleep(seconds)
        s2, t2 = p.stat().st_size, p.stat().st_mtime
        return s1 == s2 and t1 == t2
    except FileNotFoundError:
        return False


def should_skip(name: str, parent: str) -> bool:
    bad = name.startswith("~$") or "conflicted copy" in name.lower()
    bad = bad or any(name.endswith(suf) for suf in (".tmp", ".part"))
    bad = bad or name in ("desktop.ini", ".DS_Store") or parent.endswith("OneDriveTemp")
    return bad


class Handler(FileSystemEventHandler):
    def __init__(self, work_q, watch_suffixes):
        self.q, self.suffixes = work_q, set(watch_suffixes)

    def on_created(self, event):  # noqa: D401 - simple delegator
        self._maybe_queue(event)

    def on_modified(self, event):  # noqa: D401 - simple delegator
        self._maybe_queue(event)

    def _maybe_queue(self, event):
        if event.is_directory:
            return

        p = Path(event.src_path)

        if self.suffixes and p.suffix not in self.suffixes:
            return

        if should_skip(p.name, p.parent.name):
            return

        if file_is_settled(p, seconds=2):
            self.q.put(p)


def run_event_watcher(folder: str, suffixes: list[str], worker_fn):
    work_q = mp.Queue(maxsize=1024)
    handler = Handler(work_q, suffixes)
    obs = Observer()
    obs.schedule(handler, folder, recursive=False)
    obs.start()

    procs = max(mp.cpu_count() - 1, 1)

    with mp.Pool(processes=procs) as pool:
        try:
            while True:
                path = work_q.get()
                pool.apply_async(worker_fn, (Path(path),))
        except KeyboardInterrupt:
            pass
        finally:
            obs.stop()
            obs.join()

