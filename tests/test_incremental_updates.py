# Tests aligned with the current incremental update implementation.

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from incremental_updates import (
    VersionRecord,
    VersionTracker,
    build_chunk_id,
    normalize_timestamp,
    remove_previous_chunk_ids,
)


class TestVersionTrackerBasics:
    def test_version_tracker_round_trip(self, tmp_path):
        version_file = tmp_path / "versions.json"
        tracker = VersionTracker({
            "version_file": str(version_file),
            "base_dir": str(tmp_path),
        })

        source = tmp_path / "sample.txt"
        source.write_text("hello world", encoding="utf-8")

        content_hash = tracker.file_hash(source)
        tracker.mark_processed(str(source), content_hash, chunk_ids=["chunk-1"])
        tracker.mark_indexed(str(source), ["chunk-1"])

        reloaded = VersionTracker({
            "version_file": str(version_file),
            "base_dir": str(tmp_path),
        })

        assert not reloaded.needs_indexing(str(source), ["chunk-1"])
        assert not reloaded.has_changed(str(source), content_hash)

    def test_has_changed_detects_modifications(self, tmp_path):
        tracker = VersionTracker({
            "version_file": str(tmp_path / "versions.json"),
            "base_dir": str(tmp_path),
        })

        source = tmp_path / "sample.txt"
        source.write_text("original", encoding="utf-8")
        content_hash = tracker.file_hash(source)
        tracker.mark_processed(str(source), content_hash, chunk_ids=["chunk-1"])
        tracker.mark_indexed(str(source), ["chunk-1"])

        source.write_text("modified", encoding="utf-8")
        assert tracker.has_changed(str(source))

    def test_needs_indexing_detects_chunk_mismatch(self, tmp_path):
        tracker = VersionTracker({
            "version_file": str(tmp_path / "versions.json"),
            "base_dir": str(tmp_path),
        })

        source = tmp_path / "sample.txt"
        source.write_text("hello", encoding="utf-8")
        content_hash = tracker.file_hash(source)

        tracker.mark_processed(str(source), content_hash, chunk_ids=["chunk-1"])
        tracker.mark_indexed(str(source), ["chunk-1"])

        assert tracker.needs_indexing(str(source), ["chunk-1", "chunk-2"])


class TestVersionTrackerPrune:
    def test_prune_old_entries_by_age(self, tmp_path):
        tracker = VersionTracker({
            "version_file": str(tmp_path / "versions.json"),
            "base_dir": str(tmp_path),
        })

        file_path = tmp_path / "old.txt"
        file_path.write_text("content", encoding="utf-8")
        content_hash = tracker.file_hash(file_path)
        tracker.mark_processed(str(file_path), content_hash, chunk_ids=["chunk-old"])

        canonical = tracker._canonical_path(file_path)
        tracker._data["files"][canonical]["last_processed_at"] = "2020-01-01T00:00:00+00:00"

        removed = tracker.prune_old_entries(max_age_days=30)

        assert removed == 1
        assert tracker.get_record(str(file_path)) is None

    def test_prune_limits_max_entries(self, tmp_path):
        tracker = VersionTracker({
            "version_file": str(tmp_path / "versions.json"),
            "base_dir": str(tmp_path),
        })

        for idx in range(3):
            file_path = tmp_path / f"file_{idx}.txt"
            file_path.write_text(f"content {idx}", encoding="utf-8")
            content_hash = tracker.file_hash(file_path)
            tracker.mark_processed(str(file_path), content_hash, chunk_ids=[f"chunk-{idx}"])

        removed = tracker.prune_old_entries(max_entries=2)

        assert removed == 1
        remaining = tracker._data["files"].keys()
        assert len(remaining) == 2


class TestVersionTrackerPersistence:
    def test_tracker_file_structure(self, tmp_path):
        version_file = tmp_path / "versions.json"
        tracker = VersionTracker({
            "version_file": str(version_file),
            "base_dir": str(tmp_path),
        })

        file_path = tmp_path / "doc.txt"
        file_path.write_text("payload", encoding="utf-8")
        content_hash = tracker.file_hash(file_path)

        tracker.mark_processed(str(file_path), content_hash, chunk_ids=["chunk-1"])

        data = json.loads(version_file.read_text(encoding="utf-8"))
        assert "files" in data
        stored = list(data["files"].values())[0]
        assert stored["hash"] == content_hash
        assert stored["chunk_ids"] == ["chunk-1"]

    def test_get_record_returns_version_record(self, tmp_path):
        tracker = VersionTracker({
            "version_file": str(tmp_path / "versions.json"),
            "base_dir": str(tmp_path),
        })

        file_path = tmp_path / "doc.txt"
        file_path.write_text("payload", encoding="utf-8")
        content_hash = tracker.file_hash(file_path)

        tracker.mark_processed(str(file_path), content_hash, chunk_ids=["chunk-1"])
        tracker.mark_indexed(str(file_path), ["chunk-1"])

        record = tracker.get_record(str(file_path))
        assert isinstance(record, VersionRecord)
        assert record.hash == content_hash
        assert record.chunk_ids == ["chunk-1"]
        assert record.last_indexed_at is not None


class TestUtilityFunctions:
    def test_build_chunk_id_formats_name(self):
        chunk_id = build_chunk_id("2025-01-01 12:00:00", "My Document", 3)
        assert "My_Document" in chunk_id
        assert chunk_id.endswith("chunk3")

    @pytest.mark.parametrize(
        "timestamp",
        [
            "2025_01_01_12_00_00",
            "2025-01-01T12:00:00",
            "2025-01-01 12:00:00",
        ],
    )
    def test_normalize_timestamp_variants(self, timestamp):
        normalized = normalize_timestamp(timestamp)
        parsed = datetime.fromisoformat(normalized)
        assert parsed.tzinfo is not None


class DummyCollection:
    def __init__(self):
        self.deleted = []

    def delete(self, ids):
        self.deleted.extend(ids)


class DummyDedupManager:
    def __init__(self):
        self.collection = DummyCollection()
        self.hash_index = {"hash-chunk-1": {"chunk-1"}}
        self.chunk_hash_map = {"chunk-1": "hash-chunk-1"}


class TestRemovePreviousChunkIds:
    def test_remove_previous_chunk_ids_uses_dedup_manager(self):
        dedup = DummyDedupManager()
        removed = remove_previous_chunk_ids(["chunk-1"], dedup_manager=dedup)

        assert removed == 1
        assert dedup.collection.deleted == ["chunk-1"]
        assert dedup.hash_index == {}
        assert dedup.chunk_hash_map == {}

    def test_remove_previous_chunk_ids_without_ids(self):
        removed = remove_previous_chunk_ids([])
        assert removed == 0

