"""
Monitoring system for the enterprise chunker.

Provides periodic health checks for disk usage, ChromaDB availability,
and processing throughput. Integrates with the existing notification
system for alerting.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import psutil


class MonitoringSystem:
    """Background monitoring service for runtime health checks."""

    DEFAULT_DISK_THRESHOLDS = {"warning": 85, "critical": 95}
    DEFAULT_PROCESSING_RATE = {
        "enabled": True,
        "window_minutes": 15,
        "min_files_per_minute": 0.25,
        "critical_min_files_per_minute": 0.05,
    }
    DEFAULT_CHROMADB = {"enabled": True}

    def __init__(
        self,
        config: Dict[str, Any],
        db: Optional[Any] = None,
        notification_system: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.config = config
        self.db = db
        self.notification_system = notification_system
        self.logger = logger or logging.getLogger(__name__)
        self._start_time = datetime.now(timezone.utc)

        self.monitoring_config = config.get("monitoring", {}) or {}
        self.enabled: bool = bool(self.monitoring_config.get("enabled", False))
        self.interval_minutes: float = max(
            0.1, float(self.monitoring_config.get("interval_minutes", 5))
        )
        self.disk_thresholds: Dict[str, float] = {
            **self.DEFAULT_DISK_THRESHOLDS,
            **(self.monitoring_config.get("disk_thresholds") or {}),
        }
        self.processing_rate_config: Dict[str, Any] = {
            **self.DEFAULT_PROCESSING_RATE,
            **(self.monitoring_config.get("processing_rate") or {}),
        }
        self.chromadb_config: Dict[str, Any] = {
            **self.DEFAULT_CHROMADB,
            **(self.monitoring_config.get("chromadb") or {}),
        }
        self.alert_cooldown_minutes: float = float(
            self.monitoring_config.get("alert_cooldown_minutes", 10)
        )
        self.email_config: Dict[str, Any] = self.monitoring_config.get("email", {}) or {}

        watch_dir = config.get("watch_folder")
        output_dir = config.get("output_dir")
        archive_dir = config.get("archive_dir")
        self.directories: List[str] = [
            directory
            for directory in [watch_dir, output_dir, archive_dir]
            if directory
        ]

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._history_lock = threading.Lock()
        self._event_history: List[Dict[str, Any]] = []
        self._last_alerts: Dict[str, datetime] = {}

        self.logger.debug(
            "[Monitoring] Initialized (enabled=%s, interval=%s minutes)",
            self.enabled,
            self.interval_minutes,
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def start_monitoring(self) -> None:
        """Start the background monitoring thread."""
        if not self.enabled:
            self.logger.debug("[Monitoring] Monitoring disabled; start skipped.")
            return

        if self._thread and self._thread.is_alive():
            self.logger.debug("[Monitoring] Monitoring thread already running.")
            return

        self.logger.info(
            "[Monitoring] Starting monitoring thread (interval=%s minutes).",
            self.interval_minutes,
        )
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop, name="ChunkerMonitoringThread", daemon=True
        )
        self._thread.start()

    def stop_monitoring(self, timeout: Optional[float] = 5.0) -> None:
        """Request the monitoring thread to stop and wait for completion."""
        if not self._thread:
            return

        self.logger.info("[Monitoring] Stopping monitoring thread.")
        self._stop_event.set()
        self._thread.join(timeout=timeout)
        self._thread = None

    def run_checks(self) -> Dict[str, Any]:
        """Execute all configured health checks immediately."""
        results = {
            "disk": self.check_disk_space(),
            "processing_rate": self.check_processing_rate(),
            "chromadb": self.check_chromadb_health(),
        }
        return results

    def record_processing_event(
        self, success: bool, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a processing outcome for throughput tracking."""
        if not self.enabled or not self.processing_rate_config.get("enabled", True):
            return

        event = {
            "timestamp": datetime.now(timezone.utc),
            "success": bool(success),
            "metadata": metadata or {},
        }
        with self._history_lock:
            self._event_history.append(event)
            self._prune_event_history()

    def record_error(
        self, error_type: str, message: str, severity: str = "warning"
    ) -> None:
        """Record an error and escalate via alerting if configured."""
        if not self.enabled:
            return

        alert_key = f"error:{error_type}"
        detail = f"{error_type}: {message}"
        self.raise_alert("Processing Error", detail, severity=severity, alert_key=alert_key)

    # ------------------------------------------------------------------ #
    # Health checks
    # ------------------------------------------------------------------ #
    def check_disk_space(self) -> Dict[str, Any]:
        """Inspect disk utilization for configured directories."""
        if not self.directories:
            return {"status": "skipped", "message": "No directories configured."}

        status_details: List[Dict[str, Any]] = []
        overall_status = "ok"

        for directory in self.directories:
            if not os.path.exists(directory):
                detail = {
                    "path": directory,
                    "status": "skipped",
                    "message": "Directory does not exist.",
                }
                status_details.append(detail)
                continue

            try:
                usage = psutil.disk_usage(directory)
                percent = usage.percent
                severity = None
                if percent >= self.disk_thresholds.get("critical", 95):
                    severity = "critical"
                elif percent >= self.disk_thresholds.get("warning", 85):
                    severity = "warning"

                detail = {
                    "path": directory,
                    "percent": percent,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "status": severity or "ok",
                }
                status_details.append(detail)

                if severity:
                    overall_status = "critical" if severity == "critical" else "warning"
                    self.raise_alert(
                        "Disk Space",
                        f"{directory} usage at {percent:.1f}%",
                        severity=severity,
                        alert_key=f"disk:{directory}",
                    )
            except Exception as exc:  # pragma: no cover - defensive
                detail = {
                    "path": directory,
                    "status": "error",
                    "message": f"Disk usage check failed: {exc}",
                }
                status_details.append(detail)
                overall_status = "critical"
                self.raise_alert(
                    "Disk Space Check Failed",
                    f"Unable to inspect {directory}: {exc}",
                    severity="critical",
                    alert_key=f"disk:{directory}:error",
                )

        return {"status": overall_status, "details": status_details}

    def check_processing_rate(self) -> Dict[str, Any]:
        """Evaluate recent processing throughput."""
        if not self.processing_rate_config.get("enabled", True):
            return {"status": "skipped", "message": "Processing rate check disabled."}

        window_minutes = max(1, int(self.processing_rate_config.get("window_minutes", 15)))
        min_rate = max(0.0, float(self.processing_rate_config.get("min_files_per_minute", 0)))
        critical_rate = self.processing_rate_config.get("critical_min_files_per_minute")
        critical_rate = (
            float(critical_rate) if critical_rate is not None else None
        )
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

        processed_count: Optional[int] = None
        if self.db:
            conn = None
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM processing_history
                    WHERE timestamp >= ? AND success = 1
                    """,
                    (cutoff.strftime("%Y-%m-%d %H:%M:%S"),),
                )
                row = cursor.fetchone()
                processed_count = int(row[0]) if row and row[0] is not None else 0
            except Exception as exc:
                self.logger.warning(
                    "[Monitoring] Failed to query processing history: %s", exc
                )
            finally:
                if conn:
                    conn.close()

        if processed_count is None:
            with self._history_lock:
                self._prune_event_history(cutoff)
                processed_count = sum(
                    1
                    for event in self._event_history
                    if event.get("success") and event.get("timestamp") >= cutoff
                )

        rate = processed_count / window_minutes if window_minutes else float(processed_count)

        now_utc = datetime.now(timezone.utc)
        status = "ok"
        severity = None
        if processed_count == 0 and now_utc - self._start_time < timedelta(minutes=window_minutes):
            self.logger.debug(
                "[Monitoring] Processing rate warm-up period (window=%s minutes).",
                window_minutes,
            )
            return {
                "status": "warming",
                "count": processed_count,
                "rate_per_minute": rate,
                "window_minutes": window_minutes,
            }
        if critical_rate is not None and rate < critical_rate:
            status = "critical"
            severity = "critical"
        elif rate < min_rate:
            status = "warning"
            severity = "warning"

        detail_message = (
            f"{processed_count} files in last {window_minutes} minutes "
            f"(rate {rate:.2f}/min, threshold {min_rate:.2f}/min)"
        )

        if severity:
            self.raise_alert(
                "Processing Throughput",
                detail_message,
                severity=severity,
                alert_key="processing_rate",
            )
        else:
            self.logger.debug("[Monitoring] Processing rate healthy: %s", detail_message)

        return {
            "status": status,
            "count": processed_count,
            "rate_per_minute": rate,
            "window_minutes": window_minutes,
        }

    def check_chromadb_health(self) -> Dict[str, Any]:
        """Run a basic health check against the ChromaDB store."""
        if not self.chromadb_config.get("enabled", True):
            return {"status": "skipped", "message": "ChromaDB monitoring disabled."}

        if not self.config.get("rag_enabled", False):
            return {"status": "skipped", "message": "RAG integration disabled."}

        persist_dir = self.config.get("chroma_persist_dir", "./chroma_db")
        if not os.path.exists(persist_dir):
            message = f"ChromaDB directory not found: {persist_dir}"
            self.raise_alert(
                "ChromaDB Missing",
                message,
                severity="warning",
                alert_key="chromadb:missing",
            )
            return {"status": "warning", "message": message}

        try:
            import chromadb  # type: ignore
            from chromadb.config import Settings  # type: ignore
        except Exception:  # pragma: no cover - depends on optional dependency
            message = "ChromaDB client library not installed."
            self.raise_alert(
                "ChromaDB Client Missing",
                message,
                severity="warning",
                alert_key="chromadb:client_missing",
            )
            return {"status": "warning", "message": message}

        try:
            chroma_settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True,
                chroma_api_impl="chromadb.api.segment.SegmentAPI",
                chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
                chroma_producer_impl="chromadb.db.impl.sqlite.SqliteDB",
                chroma_consumer_impl="chromadb.db.impl.sqlite.SqliteDB",
                chroma_segment_manager_impl="chromadb.segment.impl.manager.local.LocalSegmentManager",
            )
            client = chromadb.PersistentClient(
                path=persist_dir,
                settings=chroma_settings,
            )
            collections = client.list_collections()
            details = {
                "status": "ok",
                "collection_count": len(collections),
                "persist_dir": persist_dir,
            }
            self.logger.debug(
                "[Monitoring] ChromaDB healthy (collections=%s).",
                len(collections),
            )
            return details
        except Exception as exc:
            message = f"ChromaDB health check failed: {exc}"
            self.raise_alert(
                "ChromaDB Health Check Failed",
                message,
                severity="critical",
                alert_key="chromadb:error",
            )
            return {"status": "critical", "message": message}

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _monitor_loop(self) -> None:
        interval_seconds = max(10.0, self.interval_minutes * 60.0)
        self.logger.debug(
            "[Monitoring] Background loop active (interval=%s seconds).",
            interval_seconds,
        )
        while not self._stop_event.is_set():
            try:
                self.run_checks()
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.error("[Monitoring] Monitoring loop error: %s", exc, exc_info=True)
            finally:
                self._stop_event.wait(interval_seconds)

    def _prune_event_history(self, cutoff: Optional[datetime] = None) -> None:
        if cutoff is None:
            window_minutes = max(
                1, int(self.processing_rate_config.get("window_minutes", 15))
            )
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

        original_length = len(self._event_history)
        self._event_history = [
            event for event in self._event_history if event.get("timestamp") >= cutoff
        ]
        if len(self._event_history) != original_length:
            self.logger.debug(
                "[Monitoring] Pruned %s stale processing events.",
                original_length - len(self._event_history),
            )

    def raise_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        alert_key: Optional[str] = None,
    ) -> None:
        """Log and optionally send alert notifications."""
        if not self.enabled:
            return

        severity = severity.lower()
        now = datetime.now(timezone.utc)
        key = alert_key or title
        last_sent = self._last_alerts.get(key)
        if (
            last_sent
            and self.alert_cooldown_minutes > 0
            and now - last_sent < timedelta(minutes=self.alert_cooldown_minutes)
        ):
            self.logger.debug(
                "[Monitoring] Suppressing alert '%s' due to cooldown.", key
            )
            return

        log_message = f"[Monitoring][{severity.upper()}] {title}: {message}"
        if severity == "critical":
            self.logger.error(log_message)
        elif severity == "warning":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        if self.notification_system:
            try:
                if hasattr(self.notification_system, "send_monitoring_alert"):
                    self.notification_system.send_monitoring_alert(
                        title, message, severity=severity
                    )
                else:
                    # Fallback to email if available
                    recipients = self.email_config.get("recipients")
                    subject = f"[Monitoring][{severity.upper()}] {title}"
                    body = f"{message}\nTime: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                    self.notification_system.send_email(recipients, subject, body)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.error(
                    "[Monitoring] Failed to send monitoring alert: %s", exc
                )

        self._last_alerts[key] = now


__all__ = ["MonitoringSystem"]


