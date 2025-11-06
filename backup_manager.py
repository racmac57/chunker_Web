import argparse
import json
import logging
import tarfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BackupManager:
    """Create and manage compressed backups for critical project assets."""

    def __init__(
        self,
        backup_config: Dict,
        global_config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.config = backup_config or {}
        self.global_config = global_config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.backup_dir = Path(self.config.get("backup_dir", "./backups")).resolve()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        include_paths = self.config.get("include_paths")
        if not include_paths:
            include_paths = self._default_include_paths()
        self.include_paths = [Path(path).resolve() for path in include_paths if path]

        self.keep_backups = max(int(self.config.get("keep_backups", 5)), 0)
        self.schedule_cfg = self.config.get("schedule", {}) or {}

        self._stop_event: Optional[threading.Event] = None
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------ #
    # Backup lifecycle                                                   #
    # ------------------------------------------------------------------ #
    def create_backup(self, label: Optional[str] = None) -> Path:
        """Create a compressed tar.gz backup of the configured include paths."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        label_suffix = f"_{label}" if label else ""
        backup_path = self.backup_dir / f"backup_{timestamp}{label_suffix}.tar.gz"

        if not self.include_paths:
            raise ValueError("No include paths configured for backup")

        self.logger.info("Starting backup: %s", backup_path)
        with tarfile.open(backup_path, mode="w:gz") as archive:
            for path in self.include_paths:
                if not path.exists():
                    self.logger.warning("Skipping missing path during backup: %s", path)
                    continue
                arcname = path.name if path.is_dir() else path.name
                archive.add(path, arcname=arcname)

        self.logger.info("Backup completed: %s", backup_path)
        self.rotate_backups()
        return backup_path

    def rotate_backups(self) -> List[Path]:
        """Remove backups exceeding the retention count."""
        if self.keep_backups <= 0:
            return []

        backups = self.list_backups()
        excess = backups[self.keep_backups :]
        for path, _ in excess:
            try:
                path.unlink()
                self.logger.info("Rotated old backup: %s", path)
            except FileNotFoundError:
                continue
            except Exception as exc:
                self.logger.error("Failed to delete backup %s: %s", path, exc)
        return [path for path, _ in excess]

    def list_backups(self) -> List[Tuple[Path, float]]:
        """Return available backups sorted newest-first."""
        backups: List[Tuple[Path, float]] = []
        for file in self.backup_dir.glob("backup_*.tar.gz"):
            backups.append((file, file.stat().st_mtime))
        backups.sort(key=lambda item: item[1], reverse=True)
        return backups

    def restore_backup(
        self,
        backup_path: Path,
        target_dir: Optional[Path] = None,
        overwrite: bool = False,
    ) -> Path:
        """Restore the provided backup archive into the target directory."""
        backup_path = Path(backup_path).resolve()
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup archive not found: {backup_path}")

        target_dir = Path(target_dir).resolve() if target_dir else Path(".").resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(backup_path, mode="r:gz") as archive:
            if not overwrite:
                self._ensure_restore_safe(archive, target_dir)
            archive.extractall(path=target_dir)

        self.logger.info("Restored backup %s to %s", backup_path, target_dir)
        return target_dir

    # ------------------------------------------------------------------ #
    # Scheduling                                                         #
    # ------------------------------------------------------------------ #
    def schedule_backups(
        self,
        *,
        interval_seconds: Optional[float] = None,
        run_immediately: bool = False,
    ) -> Optional[threading.Thread]:
        """Start a background scheduler to create backups on an interval."""
        if self._thread and self._thread.is_alive():
            return self._thread

        interval = interval_seconds or self._schedule_interval_seconds()
        if not interval or interval <= 0:
            self.logger.warning("Skipped scheduling backups: invalid interval %s", interval)
            return None

        self._stop_event = threading.Event()

        def _worker() -> None:
            initial_delay = self._initial_delay_seconds(run_immediately)
            if initial_delay > 0 and self._stop_event and self._stop_event.wait(initial_delay):
                return

            while self._stop_event and not self._stop_event.is_set():
                try:
                    self.create_backup()
                except Exception as exc:  # pragma: no cover - safety logging
                    self.logger.exception("Scheduled backup failed: %s", exc)
                if self._stop_event.wait(interval):
                    break

        self._thread = threading.Thread(
            target=_worker, name="BackupScheduler", daemon=True
        )
        self._thread.start()
        self.logger.info("Scheduled backups every %s seconds", interval)
        return self._thread

    def stop_scheduled_backups(self, timeout: float = 5.0) -> None:
        if self._stop_event:
            self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                self.logger.warning("Backup scheduler thread did not terminate cleanly")
        self._stop_event = None
        self._thread = None

    # ------------------------------------------------------------------ #
    # Internal utilities                                                 #
    # ------------------------------------------------------------------ #
    def _default_include_paths(self) -> List[str]:
        paths: List[str] = []
        chroma_dir = self.global_config.get("chroma_persist_dir")
        watch_dir = self.global_config.get("watch_folder")
        output_dir = self.global_config.get("output_dir")
        archive_dir = self.global_config.get("archive_dir")

        for candidate in (chroma_dir, output_dir, archive_dir, watch_dir):
            if candidate:
                paths.append(candidate)
        config_path = Path("config.json")
        if config_path.exists():
            paths.append(str(config_path))
        return paths

    def _schedule_interval_seconds(self) -> Optional[float]:
        interval_hours = self.schedule_cfg.get("interval_hours")
        if interval_hours is not None:
            return float(interval_hours) * 3600.0
        interval_minutes = self.schedule_cfg.get("interval_minutes")
        if interval_minutes is not None:
            return float(interval_minutes) * 60.0
        return None

    def _initial_delay_seconds(self, run_immediately: bool) -> float:
        if run_immediately:
            return 0.0
        startup_delay_minutes = self.schedule_cfg.get("startup_delay_minutes", 0)
        if startup_delay_minutes:
            return float(startup_delay_minutes) * 60.0

        hour = self.schedule_cfg.get("hour")
        if hour is None:
            return 0.0

        now = datetime.now()
        target = now.replace(hour=int(hour), minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return (target - now).total_seconds()

    def _ensure_restore_safe(self, archive: tarfile.TarFile, target_dir: Path) -> None:
        members = archive.getmembers()
        conflicts: List[str] = []
        for member in members:
            target_path = target_dir / member.name
            if target_path.exists():
                conflicts.append(str(target_path))
        if conflicts:
            conflict_str = "\n".join(conflicts)
            raise FileExistsError(
                "Restore would overwrite existing files. "
                "Set overwrite=True to force restore.\n"
                f"Conflicts:\n{conflict_str}"
            )

    # ------------------------------------------------------------------ #
    # CLI helper                                                         #
    # ------------------------------------------------------------------ #
    @staticmethod
    def load_config(path: Path) -> Dict:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backup manager CLI")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parent / "config.json"),
        help="Path to configuration file (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available backups")

    create_parser = subparsers.add_parser("create", help="Create a new backup")
    create_parser.add_argument("--label", help="Optional label appended to backup filename")

    rotate_parser = subparsers.add_parser("rotate", help="Rotate backups based on retention")
    rotate_parser.add_argument(
        "--keep",
        type=int,
        help="Override retention count for this rotation run",
    )

    restore_parser = subparsers.add_parser("restore", help="Restore a backup archive")
    restore_parser.add_argument("backup_path", help="Path to the backup .tar.gz file")
    restore_parser.add_argument(
        "--target",
        help="Directory to extract backup contents into (default: current directory)",
    )
    restore_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow existing files to be overwritten during restore",
    )

    return parser


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    parser = _build_cli()
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    full_config = BackupManager.load_config(config_path)
    backup_config = full_config.get("backup", {})
    manager = BackupManager(backup_config, full_config)

    if args.command == "list":
        backups = manager.list_backups()
        if not backups:
            print("No backups found.")
        for path, mtime in backups:
            size_mb = path.stat().st_size / (1024 * 1024)
            timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{path} | {size_mb:.2f} MiB | {timestamp}")
    elif args.command == "create":
        backup_path = manager.create_backup(label=args.label)
        print(f"Backup created: {backup_path}")
    elif args.command == "rotate":
        if args.keep is not None:
            manager.keep_backups = max(args.keep, 0)
        removed = manager.rotate_backups()
        if removed:
            print("Removed backups:")
            for path in removed:
                print(f" - {path}")
        else:
            print("No backups removed.")
    elif args.command == "restore":
        target = Path(args.target).resolve() if args.target else None
        restored_dir = manager.restore_backup(
            Path(args.backup_path), target_dir=target, overwrite=args.overwrite
        )
        print(f"Backup restored to: {restored_dir}")
    else:  # pragma: no cover
        parser.print_help()


if __name__ == "__main__":
    main()

