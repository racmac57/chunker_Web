from types import SimpleNamespace

import pytest

from monitoring_system import MonitoringSystem


class TestMonitoringBasics:
    def test_run_checks_returns_sections_when_disabled(self, tmp_path):
        config = {
            "monitoring": {"enabled": False},
            "watch_folder": str(tmp_path),
        }
        monitor = MonitoringSystem(config)

        results = monitor.run_checks()

        assert set(results.keys()) == {"disk", "processing_rate", "chromadb"}
        assert results["disk"]["status"] in {"ok", "skipped", "warning", "critical"}


class TestDiskChecks:
    def test_check_disk_space_warning_triggers_alert(self, tmp_path, monkeypatch):
        config = {
            "monitoring": {
                "enabled": True,
                "disk_thresholds": {"warning": 50, "critical": 90},
            },
            "watch_folder": str(tmp_path),
        }
        monitor = MonitoringSystem(config)

        class FakeUsage(SimpleNamespace):
            pass

        fake_usage = FakeUsage(percent=85, total=1, used=1, free=0)
        monkeypatch.setattr("psutil.disk_usage", lambda path: fake_usage)

        alerts = []

        def capture_alert(title, message, severity, alert_key=None):
            alerts.append(severity)

        monitor.raise_alert = capture_alert

        result = monitor.check_disk_space()

        assert result["status"] == "warning"
        assert alerts == ["warning"]


class TestProcessingRate:
    def test_processing_rate_uses_event_history(self):
        config = {
            "monitoring": {
                "enabled": True,
                "processing_rate": {
                    "enabled": True,
                    "window_minutes": 1,
                    "min_files_per_minute": 2,
                },
            }
        }
        monitor = MonitoringSystem(config)

        monitor.record_processing_event(success=True)
        monitor.record_processing_event(success=True)

        result = monitor.check_processing_rate()

        assert result["count"] >= 2
        assert result["status"] in {"ok", "warning"}

    def test_processing_rate_disabled_returns_skipped(self):
        config = {
            "monitoring": {
                "enabled": True,
                "processing_rate": {"enabled": False},
            }
        }
        monitor = MonitoringSystem(config)

        result = monitor.check_processing_rate()

        assert result["status"] == "skipped"


class TestAlerting:
    def test_raise_alert_respects_cooldown(self):
        config = {
            "monitoring": {
                "enabled": True,
                "alert_cooldown_minutes": 10,
            }
        }
        monitor = MonitoringSystem(config)

        sent = []

        def fake_logger(message):
            sent.append(message)

        monitor.logger.warning = fake_logger
        monitor.logger.error = fake_logger
        monitor.logger.info = fake_logger

        monitor.raise_alert("Test", "message", severity="warning", alert_key="test")
        monitor.raise_alert("Test", "message", severity="warning", alert_key="test")

        assert len(sent) == 1


class TestChromaCheck:
    def test_chromadb_check_skipped_when_rag_disabled(self, tmp_path):
        config = {
            "monitoring": {"enabled": True, "chromadb": {"enabled": True}},
            "rag_enabled": False,
            "chroma_persist_dir": str(tmp_path / "missing"),
        }
        monitor = MonitoringSystem(config)

        result = monitor.check_chromadb_health()

        assert result["status"] == "skipped"

