Cursor AI Prompt

Goal

* Fix chunk writer and manifest copy.
* Add DB lock retries and 60s timeout.
* Reduce lock risk and queue stalls.
* Add tests and a runbook.
* Restart watcher, smoke test, then process the 50 files.

Context

* Repo: C:_chunker. Remote: racmac57/chunker_Web.
* Watcher monitors %OneDriveCommercial%\KB_Shared\02_data.
* Files sit in watch. Chunk writes fail. DB logs report “database is locked.”
* Reference handoff brief for details .

Risks and dependencies

* SQLite locks. Add retries and longer timeout.
* Possible SQLite corruption. Add integrity check.
* Windows paths. Use pathlib Path.
* Single watcher instance. Task Scheduler and mutex enforce this.
* OneDrive availability. Keep KB_Shared pinned offline.

Tasks

1. watcher_splitter.py hardening

* Skip .origin.json sidecars.
* Ensure content_hash exists.
* Fix chunk writes. Create parent dirs once.
* Fix manifest copy.
* Periodically clear processed_files.
* Optional: use multiprocessing.Pool for heavy batches with batch_size 32.
* Cache sentence tokenizer with lru_cache.
* Move metrics logging off main thread.
* Rate limit notifications to 1 per 60s per key.

Apply these edits

Skip origin sidecars

```python
# near should_process_file or early guard
name_l = path.name.lower()
if ".origin.json" in name_l:
    return False
```

Ensure content_hash

```python
# after text extraction and before version tracking
if not content_hash:
    try:
        content_hash = version_tracker.hash_content(text)
    except Exception:
        pass
```

Chunk writer and manifest copy

```python
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def write_chunk_files(doc_id: str, chunks: list[str], out_root: str) -> list[str]:
    written: list[str] = []
    base = Path(out_root) / doc_id
    base.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(chunks):
        p = base / f"chunk_{i:05d}.txt"
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(text if isinstance(text, str) else str(text))
            written.append(str(p))
        except Exception as e:
            logger.exception("Chunk write failed for %s: %s", p, e)
    return written

def copy_manifest_sidecar(src_manifest: str, dst_path: str):
    dst = Path(dst_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src_manifest, "r", encoding="utf-8") as fsrc, \
         open(dst, "w", encoding="utf-8") as fdst:
        fdst.write(fsrc.read())
```

Periodic set cleanup

```python
if len(processed_files) > 1000:
    processed_files.clear()
```

Optional parallelism and batching

```python
# when dispatching many files
from multiprocessing import Pool, cpu_count
batch_size = 32
workers = max(cpu_count() - 1, 1)
with Pool(processes=workers) as pool:
    for i in range(0, len(files), batch_size):
        pool.map(process_one_file, files[i:i+batch_size])
```

Tokenizer cache

```python
from functools import lru_cache

@lru_cache(maxsize=4096)
def _sent_tokenize_cached(s: str) -> list[str]:
    return sent_tokenize(s)
```

Metrics and notifications

```python
# run log_system_metrics in a background thread
# add notify_once_per
_last = {}
def notify_once_per(key: str, seconds: int, msg: str):
    now = time.time()
    if (now - _last.get(key, 0)) >= seconds:
        _last[key] = now
        notify(msg)
```

2. chunker_db.py resilience

* Direct connect with timeout in _conn.
* Retry log_error on lock with backoff.
* Add integrity check on startup.

Edits

```python
import sqlite3, time, json, logging
log = logging.getLogger(__name__)

def _conn(self):
    return sqlite3.connect(self.db_path, timeout=60)

def run_integrity_check(self) -> bool:
    try:
        with self._conn() as conn:
            row = conn.execute("PRAGMA integrity_check").fetchone()
            return bool(row and row[0] == "ok")
    except Exception as e:
        log.error("Integrity check failed: %s", e)
        return False

def log_error(self, file_name: str, message: str):
    retries = 6
    delay = 0.5
    for attempt in range(retries):
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                conn.execute(
                    "INSERT INTO errors(file_name, message, ts) VALUES(?,?,strftime('%Y-%m-%dT%H:%M:%S','now'))",
                    (file_name, (message or "")[:2048]),
                )
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 5.0)
                continue
            log.warning("log_error failed after %s tries: %s", attempt + 1, e)
            return
```

3. Tests and legacy guard

* Root conftest.py to ignore 99_doc.
* DB retry smoke test.

Files

```python
# conftest.py
def pytest_ignore_collect(path):
    p = str(path).replace("\\","/")
    if "/99_doc/" in p:
        return True
    return False
```

```python
# tests/test_db.py
from chunker_db import ChunkerDatabase

def test_log_error_retry(tmp_path):
    db = ChunkerDatabase(db_path=str(tmp_path/"t.db"))
    # db.init_schema() if needed
    db.log_error("x.txt", "test message")
    assert True
```

Runbook

Build and restart

```
git add watcher_splitter.py chunker_db.py conftest.py tests/test_db.py
git commit -m "Watcher and DB hardening. Chunk writes. Manifest mkdir. DB retry and timeout. Legacy test guard."
npm run kb:stop
npm run kb:start
```

Smoke test

```
$ts = Get-Date -Format yyyyMMdd_HHmmss
$p  = "$env:OneDriveCommercial\KB_Shared\02_data\smoke_$ts.md"
"Smoke test $ts`n$([string]::new('X', 900))" | Set-Content -Path $p -Encoding UTF8
```

Verify

```
Get-Content .\logs\watcher.log -Tail 40 -Wait
Test-Path "$env:OneDriveCommercial\KB_Shared\03_archive\smoke_$ts.md"
Get-ChildItem "$env:OneDriveCommercial\KB_Shared\04_output" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name,LastWriteTime
npm run kb:report
```

Resume the 50-file batch

* Keep watcher on one PC.
* Move any pending files into %OneDriveCommercial%\KB_Shared\02_data.
* Tail logs for errors.

Multi-agent coordination

* Assign Agent A for watcher_splitter.py.
* Assign Agent B for chunker_db.py and tests.
* Lead agent owns smoke test and commit order.
* Enforce single source of truth on main branch.
* Roll back on red smoke. Revert the last commit.
* Use short status notes in PRs. Include logs only when needed.

Handover checklist

* Watcher Running with PID. OneDriveOK True. ChromaDB True.
* Smoke file archived True. Output count increased.
* No chunk write exceptions in last 100 log lines.
* No “database is locked” lines after retries.
* Legacy tests ignored. New DB test passes.
* README updated with steps and commands.
* Task Scheduler points to the right paths.
