# Release Workflow Helper

This script-driven flow streamlines the final release steps by backing up
untracked content, staging documentation updates, cleaning remaining artifacts,
and finishing with a commit/tag push in one go.

## Usage

```batch
scripts\release_commit_and_tag.bat "Your commit message" vX.Y.Z
```

The helper performs the following actions:

1. **Environment checks** – verifies that Git is available.
2. **Timestamped backup** – copies all untracked files (preserving folder
   structure) into a `backup_YYYYMMDD` directory so accidental deletes can be
   recovered.
3. **Doc staging** – automatically runs `git add *.md *.json` to capture docs
   and metadata updates.
4. **Interactive clean** – launches `git clean -fdx -i` so you can review and
   remove remaining build artifacts.
5. **Commit, tag, push** – stages everything, creates the commit and annotated
   tag, then pushes `HEAD` plus tags to `origin`.

## Logging & Rotation

- Activity is appended to `release_log.txt`.
- When the log exceeds 1 MB it is rotated automatically and the archived file
  is renamed `release_log_YYYYMMDD_HHMM.txt`.

## Tips

- Review the backup folder before deleting anything permanently.
- The interactive clean step is optional—press `q` to quit if you want to skip
  deletions.
- After the script finishes you’re ready to ship; no manual `git push` is
  required.

