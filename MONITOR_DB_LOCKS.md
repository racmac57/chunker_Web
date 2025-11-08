# Database Lock Error Monitoring Plan

## Baseline Metrics (2025-11-07 18:24-18:32)
- Duration: 8 minutes
- Total lock errors: 11 log_processing + 1 dept_stats = **12 errors**
- Rate: **1.5 errors/minute** (down 68% from pre-fix baseline)
- Complete failures: 1 dept_stats failure after 5 retries

## Monitoring Commands

### Real-time tail (keep this running in separate terminal)
```bash
powershell -Command "Get-Content watcher_live.log -Wait | Select-String -Pattern 'Failed to log|database is locked|Department stats'"
```

### Hourly error count
```bash
powershell -Command "(Get-Content watcher_live.log | Select-String -Pattern 'Failed to log processing' | Select-Object -Last 100 | Select-String -Pattern (Get-Date).ToString('yyyy-MM-dd HH:') | Measure-Object).Count"
```

### Error rate over time (run every 4 hours)
```bash
powershell -Command "Get-Content watcher_live.log | Select-String -Pattern 'Failed to (log|update)' | Select-Object -Last 50"
```

## Alert Thresholds

| Metric | Current | Alert If Exceeds |
|--------|---------|------------------|
| Lock errors per minute | 1.5 | **> 3.0** (2x baseline) |
| Dept stats complete failures | 1/8min | **> 3/hour** |
| Consecutive lock errors | 3-4 | **> 10** |

## Pattern Analysis (Check every 8-12 hours)

### 1. Time-based clustering
```bash
# Extract error timestamps and look for patterns
powershell -Command "Get-Content watcher_live.log | Select-String -Pattern 'Failed to log processing' | ForEach-Object { $_.Line.Substring(0,19) } | Group-Object | Sort-Object Count -Descending | Select-Object -First 10"
```

**Look for:** Errors clustering at specific times (e.g., 2:00 AM if scheduled jobs run)

### 2. Processing volume correlation
```bash
# Check if errors spike during heavy processing
powershell -Command "Get-Content watcher_live.log | Select-String -Pattern 'Processing \d+ files with \d+ workers' | Select-Object -Last 20"
```

**Look for:** High worker count (4 workers) coinciding with lock error bursts

### 3. Error duration analysis
```bash
# Check time spans between lock error clusters
powershell -Command "Get-Content watcher_live.log | Select-String -Pattern 'Failed to log' | Select-Object -First 1 -Last 1"
```

**Look for:** Sustained periods (> 5 minutes) of continuous lock errors

## Action Items Based on Monitoring

### If error rate spikes > 3.0/minute:
1. **Short-term:** Temporarily reduce parallel workers from 4 to 2
   ```python
   # In watcher_splitter.py, line ~1016
   max_workers = min(2, cpu_count())  # Reduce from 4
   ```

2. **Medium-term:** Implement retry logic in `log_processing()` method (chunker_db.py:106)

### If dept stats failures > 3/hour:
1. Increase `max_retries` from 5 to 7 in `_update_department_stats()`
2. Increase initial `retry_delay` from 1.0s to 1.5s

### If errors cluster at specific times:
- Identify conflicting processes (backups, scheduled tasks)
- Consider staggering watcher scan intervals to avoid overlap
- Implement connection pooling (requires larger refactor)

## Long-term Improvements (Consider if baseline stays > 2/min)

1. **Add retry wrapper to log_processing()** (chunker_db.py:106)
   - Similar to `_update_department_stats()` pattern
   - Use 3 retries, 0.5s → 0.75s → 1.125s backoff

2. **Separate database for logs vs. stats**
   - Write-heavy operations (logs) → separate DB
   - Reduces contention on stats queries

3. **Implement write queue**
   - Buffer log entries in memory
   - Batch-write every 5-10 seconds
   - Reduces transaction frequency

4. **Connection pooling**
   - Maintain 2-3 persistent connections
   - Rotate usage to reduce open/close overhead

## Review Schedule

- **Hour 8:** Run pattern analysis, check for time clustering
- **Hour 16:** Review error rate trend, compare to baseline
- **Hour 24:** Full analysis, decide if action needed
- **Hour 48:** Final assessment, document new baseline

---

**Next Agent Handoff:** If monitoring shows sustained > 3 errors/minute or frequent dept_stats failures, implement retry logic in `log_processing()` method as described above.
