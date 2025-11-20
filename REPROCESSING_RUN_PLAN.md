## Reprocessing Run Plan – Failed Files & OneDrive Output

### 1. Current State (as of 2025-11-20 ~17:45)

- **Config** (`config.json`):
  - `watch_folder`: `C:\_chunker\02_data`
  - `output_dir`: `%OneDriveCommercial%\KB_Shared\04_output`
  - `archive_dir`: `%OneDriveCommercial%\KB_Shared\03_archive`
  - `failed_dir`: `%OneDriveCommercial%\KB_Shared\03_archive\failed`
  - `supported_extensions`: `.txt,.md,.csv,.json,.py,.m,.dax,.ps1,.sql,.pdf,.xlsx,.xls,.slx`
  - `min_file_size_bytes`: **100** (tiny files are archived to `03_archive/skipped_files/` instead of being processed)
  - Deduplication: `enabled=true`, `auto_remove=true`, `log_only=false`

- **Failed directory** (`03_archive\failed`):
  - **4,432** failed reprocess files still present (historical, all named `reprocess_...`)
  - `analyze_failed_files.py` classifies:
    - 2,931 potentially repairable
    - 1,501 likely permanent (unsupported, too large, or very old)

- **Batch reprocessing script** (`batch_reprocess_failed.py`):
  - Last run: `python batch_reprocess_failed.py --all --execute`
  - Latest `05_logs\batch_reprocess_stats.json`:
    - `retryable`: **2,160**
    - `permanent_chunk`: 2,272 (Oct 27 incident chunk files)
    - `permanent_tracker`: 0
    - `skipped_backoff`: 0
    - `attempted`: **2,160**
    - `success`: **2,160** (all queued to `source`)
    - `failed`: 0

- **Source queue** (`C:\_chunker\source`):
  - **2,160** `reprocess_...` files currently queued for processing by the watcher.

- **Watcher logs**:
  - `logs\watcher.log`: currently 0 bytes (new log, active watchers write here).
  - Recent activity is in the `watcher_archive_*.log` files, confirming that:
    - Backup/temp files (`*_backup*`, `*_temp*`) are being skipped.
    - `.origin.json` manifests are being skipped.

- **02_data status** (`C:\_chunker\02_data`):
  - 5 non-origin files (backup/templates) + 6 origin manifests; all intentionally skipped by watcher.
  - No `reprocess_*` source files remain there; the reprocess queue is now in `source\`.

---

### 2. Goal When You Can Let It Run

When you have a block of time to let the process run unattended, you want to:

1. **Process all 2,160 queued retryable failed files** through the enhanced pipeline (PDF/XLSX/XLS/SLX, advanced tagging, tracker).
2. **Send successful outputs to OneDrive**:
   - Chunks/transcripts → `%OneDriveCommercial%\KB_Shared\04_output`
   - Reprocessed originals → `%OneDriveCommercial%\KB_Shared\03_archive\{department}`
3. **Leave permanent failures** tracked in `failed_file_tracker` and/or `03_archive\failed` for later review.

---

### 3. Step-by-Step When You’re Ready

#### Step 1 – Start the watcher on this laptop

Use **PowerShell**, not cmd:

```powershell
cd C:\_chunker
python watcher_splitter.py
```

- Leave this window open; this is the long-running watcher.
- It will:
  - Watch `02_data\` / `source\` (according to your current flow).
  - Pick up the 2,160 `reprocess_...` files in `source\` and process them.
  - Write outputs to OneDrive `04_output\...` and archive originals to `03_archive\{department}\...`.

> Only one watcher instance should be running (on this laptop).

#### Step 2 – Let it run until the queue drains

After some time (likely a few hours, depending on file sizes), open a **second PowerShell window**:

```powershell
cd C:\_chunker

# Check how many files are still queued in source
python -c "from pathlib import Path; p = Path('source'); files = [f for f in p.glob('*') if f.is_file()]; print('Files queued in source:', len(files))"
```

- When this prints:

  ```text
  Files queued in source: 0
  ```

  …all queued `reprocess_*` files have been handed off to the watcher and processed (either successfully or as failures).

#### Step 3 – Check batch stats

Still in `C:\_chunker`:

```powershell
cd C:\_chunker
powershell -Command "Get-Content '05_logs\batch_reprocess_stats.json'"
```

Look for:

- `batch_processing.attempted` → should be 2,160
- `batch_processing.success`   → 2,160 (all queued)
- `batch_processing.failed`    → 0

This confirms the **batch script** successfully queued all retryable failures into `source\`.

#### Step 4 – Check failure tracker (optional but useful)

```powershell
cd C:\_chunker
python failed_file_tracker.py --stats
```

You may still hit the pretty-print `TypeError` for recent failures, but the top counters are what matter:

- `Total Failed`
- `Permanent Failures`
- `Retryable Failures`

If, after the watcher run, `Retryable Failures` is **0**, that means:

- Any file that still fails is now considered **permanent**, and will not be retried.

#### Step 5 – Spot‑check OneDrive outputs

Use File Explorer on this laptop and check:

- `C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\04_output`
- `C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\03_archive`

Confirm:

- New session folders with recent timestamps in `04_output\`.
- Matching `reprocess_...` source files in appropriate department subfolders in `03_archive\`.

---

### 4. Confirming “We Reprocessed as Many as Possible”

After the watcher has had time to run and `source\` is empty:

1. **Verify queue is empty**:

   ```powershell
   cd C:\_chunker
   python -c "from pathlib import Path; p = Path('source'); files = [f for f in p.glob('*') if f.is_file()]; print('Files queued in source:', len(files))"
   ```

   - Expect: `Files queued in source: 0`

2. **Re-run failed-file analysis (for context)**:

   ```powershell
   cd C:\_chunker
   python analyze_failed_files.py
   ```

   - This will still report **4,432 files** in `03_archive\failed` because it’s just analyzing the folder contents.
   - Treat these as **historical artifacts** once the tracker shows no remaining retryable failures.

3. **Use `failed_file_tracker.py --stats`**:

   ```powershell
   cd C:\_chunker
   python failed_file_tracker.py --stats
   ```

   - Focus on:
     - `Total Failed`
     - `Permanent Failures`
     - `Retryable Failures`
   - Goal: `Retryable Failures == 0` after the run.

If all of the following are true:

- `source\` is empty,
- The batch stats show the 2,160 were attempted/queued,
- The watcher has been allowed to run long enough without a backlog,
- The tracker shows **no remaining retryable failures**,

…then you have effectively **reprocessed as many of the 4,432 failed sessions as the enhanced pipeline can handle**, and all successes will be in OneDrive (`04_output` + `03_archive`).

At that point, the remaining entries in `03_archive\failed` are **permanent or historical**, not open work.

---

### 5. Optional Cleanups (After Everything is Done)

Once you’re satisfied:

- Optionally **move** the old `C:\_chunker\03_archive\failed` files into a dated subfolder, e.g.:

  ```powershell
  cd C:\_chunker
  mkdir 03_archive\failed_historical_2025_11_20
  Move-Item 03_archive\failed\* 03_archive\failed_historical_2025_11_20\
  ```

  (Skip this if you want to keep the current layout.)

- Optionally clean `02_data\` of remaining backup/template files (`*_backup*`, `*template_cleanup_vba*`, etc.), since the watcher excludes them anyway.

---

### 6. Ultra‑Short Checklist (when you’re ready to run)

1. Open **PowerShell** as you, then:

   ```powershell
   cd C:\_chunker
   python watcher_splitter.py
   ```

   Leave it running.

2. After a few hours (or next day), in a new window:

   ```powershell
   cd C:\_chunker
   python -c "from pathlib import Path; p = Path('source'); files = [f for f in p.glob('*') if f.is_file()]; print('Files queued in source:', len(files))"
   powershell -Command "Get-Content '05_logs\batch_reprocess_stats.json'"
   python failed_file_tracker.py --stats
   ```

3. Optionally spot‑check OneDrive `KB_Shared\04_output` and `KB_Shared\03_archive` to confirm new sessions.\n

{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}