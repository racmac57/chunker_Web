import tarfile
import time
from pathlib import Path

import pytest

from backup_manager import BackupManager


def _make_manager(tmp_path: Path, keep: int = 3) -> BackupManager:
    include_dir = tmp_path / "include"
    include_dir.mkdir()
    (include_dir / "sample.txt").write_text("data", encoding="utf-8")

    return BackupManager({
        "backup_dir": str(tmp_path / "backups"),
        "include_paths": [str(include_dir)],
        "keep_backups": keep,
    })


class TestBackupCreation:
    def test_create_backup_creates_tarball(self, tmp_path):
        manager = _make_manager(tmp_path)

        backup_path = manager.create_backup(label="test")

        assert backup_path.exists()
        assert backup_path.suffixes[-2:] == [".tar", ".gz"]

        with tarfile.open(backup_path, "r:gz") as archive:
            names = archive.getnames()
            assert "include" in names or "sample.txt" in "".join(names)


class TestBackupRotation:
    def test_rotation_respects_retention(self, tmp_path):
        manager = _make_manager(tmp_path, keep=2)

        for idx in range(3):
            (tmp_path / "include" / "sample.txt").write_text(f"data {idx}", encoding="utf-8")
            manager.create_backup(label=f"v{idx}")
            time.sleep(0.01)

        backups = manager.list_backups()
        assert len(backups) == 2
        backup_names = [path.name for path, _ in backups]
        assert any("v1" in name for name in backup_names)
        assert any("v2" in name for name in backup_names)

    def test_rotate_backups_returns_removed_paths(self, tmp_path):
        manager = _make_manager(tmp_path, keep=3)

        for idx in range(3):
            manager.create_backup(label=f"v{idx}")
            time.sleep(0.01)

        manager.keep_backups = 1
        removed = manager.rotate_backups()

        assert len(removed) == 2
        assert all(path.exists() is False for path in removed)


class TestBackupRestore:
    def test_restore_backup_detects_conflicts(self, tmp_path):
        manager = _make_manager(tmp_path)
        backup_path = manager.create_backup()

        target = tmp_path / "restore"
        target.mkdir()
        (target / "include").mkdir()
        (target / "include" / "sample.txt").write_text("existing", encoding="utf-8")

        with pytest.raises(FileExistsError):
            manager.restore_backup(backup_path, target_dir=target, overwrite=False)

    def test_restore_backup_with_overwrite(self, tmp_path):
        manager = _make_manager(tmp_path)
        backup_path = manager.create_backup()

        target = tmp_path / "restore"
        target.mkdir()
        (target / "include").mkdir()
        (target / "include" / "sample.txt").write_text("existing", encoding="utf-8")

        restored_dir = manager.restore_backup(backup_path, target_dir=target, overwrite=True)

        assert restored_dir.exists()
        content = (restored_dir / "include" / "sample.txt").read_text(encoding="utf-8")
        assert content == "data"


class TestBackupListing:
    def test_list_backups_sorted_newest_first(self, tmp_path):
        manager = _make_manager(tmp_path)

        first = manager.create_backup(label="first")
        time.sleep(0.01)
        second = manager.create_backup(label="second")

        backups = manager.list_backups()
        assert backups[0][0] == second
        assert backups[1][0] == first

