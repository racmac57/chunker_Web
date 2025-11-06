# notification_system.py
# Notification system for enterprise chunker

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os

class NotificationSystem:
    def __init__(self, config_file="notification_config.json"):
        self.config = self._load_config(config_file)
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file):
        """Load notification configuration"""
        default_config = {
            "enable_notifications": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "admin_emails": ["admin@example.com"],
            "from_email": "chunker@example.com",
            "enable_threshold_alerts": True,
            "enable_error_alerts": True,
            "enable_daily_reports": True,
            "enable_monitoring_alerts": True,
            "monitoring_recipients": [],
            "thresholds": {
                "cpu_warning": 80,
                "cpu_critical": 90,
                "memory_warning": 80,
                "memory_critical": 90,
                "disk_warning": 85,
                "disk_critical": 95
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logging.warning(f"Could not load notification config: {e}")
        
        return default_config
    
    def send_email(self, recipients, subject, body, html_body=None):
        """Send email notification"""
        if not self.config.get("enable_notifications", False):
            self.logger.debug("Notifications disabled, skipping email")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.get("from_email", "chunker@example.com")
            msg['To'] = ", ".join(recipients) if isinstance(recipients, list) else recipients
            
            # Add text and HTML parts
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls()
                if self.config.get("smtp_username") and self.config.get("smtp_password"):
                    server.login(self.config["smtp_username"], self.config["smtp_password"])
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {recipients}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def send_monitoring_alert(self, title, message, severity="warning"):
        """Send monitoring alert notification."""
        if not self.config.get("enable_monitoring_alerts", True):
            self.logger.debug("Monitoring alerts disabled; skipping email")
            return False
        
        recipients = (
            self.config.get("monitoring_recipients")
            or self.config.get("admin_emails", [])
        )
        if not recipients:
            self.logger.warning("No recipients configured for monitoring alerts")
            return False
        
        severity = (severity or "warning").lower()
        prefix_map = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️",
        }
        subject_prefix = prefix_map.get(severity, "⚠️")
        subject = f"{subject_prefix} Monitoring Alert: {title}"
        body = (
            f"Chunker Monitoring Alert\n\n"
            f"Title: {title}\n"
            f"Severity: {severity.upper()}\n"
            f"Message: {message}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "This is an automated monitoring alert from the Enterprise Chunker system."
        )
        
        return self.send_email(recipients, subject, body)
    
    def send_threshold_alert(self, metric_name, current_value, threshold, severity):
        """Send threshold alert"""
        if not self.config.get("enable_threshold_alerts", True):
            return False
        
        subject = f"🚨 {severity.upper()} Alert: {metric_name}"
        body = f"""
Chunker System Alert

Metric: {metric_name}
Current Value: {current_value}
Threshold: {threshold}
Severity: {severity.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated alert from the Enterprise Chunker system.
"""
        
        return self.send_email(self.config["admin_emails"], subject, body)
    
    def send_error_alert(self, error_message, filename=None, stack_trace=None):
        """Send error alert"""
        if not self.config.get("enable_error_alerts", True):
            return False
        
        subject = "❌ Chunker System Error"
        body = f"""
Chunker System Error Alert

Error: {error_message}
File: {filename or 'N/A'}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if stack_trace:
            body += f"Stack Trace:\n{stack_trace}\n"
        
        body += "\nThis is an automated alert from the Enterprise Chunker system."
        
        return self.send_email(self.config["admin_emails"], subject, body)
    
    def send_daily_summary(self, session_stats, analytics):
        """Send daily summary report"""
        if not self.config.get("enable_daily_reports", True):
            return False
        
        subject = "📊 Daily Chunker System Report"
        
        # Create summary text
        body = f"""
Daily Chunker System Report
{datetime.now().strftime('%Y-%m-%d')}

Session Statistics:
- Files Processed: {session_stats.get('files_processed', 0)}
- Chunks Created: {session_stats.get('chunks_created', 0)}
- Zero-byte Prevented: {session_stats.get('zero_byte_prevented', 0)}
- Errors: {session_stats.get('errors', 0)}
- Total Sentences: {session_stats.get('total_sentences_processed', 0)}
- Total Bytes: {session_stats.get('total_bytes_created', 0):,}

Performance Metrics:
- Average Processing Time: {session_stats.get('performance_metrics', {}).get('avg_processing_time', 0):.2f}s
- Peak CPU Usage: {session_stats.get('performance_metrics', {}).get('peak_cpu_usage', 0):.1f}%
- Peak Memory Usage: {session_stats.get('performance_metrics', {}).get('peak_memory_usage', 0):.1f}%

Department Breakdown:
"""
        
        for dept, stats in session_stats.get('department_breakdown', {}).items():
            body += f"- {dept}: {stats.get('files', 0)} files, {stats.get('chunks', 0)} chunks, {stats.get('errors', 0)} errors\n"
        
        if analytics:
            body += f"\nAnalytics (Last 24h):\n"
            processing = analytics.get('processing', {})
            body += f"- Total Files: {processing.get('total_files', 0)}\n"
            body += f"- Successful: {processing.get('successful_files', 0)}\n"
            body += f"- Total Chunks: {processing.get('total_chunks', 0)}\n"
            body += f"- Avg Processing Time: {processing.get('avg_processing_time', 0):.2f}s\n"
            
            if analytics.get('errors'):
                body += f"\nError Summary:\n"
                for error_type, count in analytics['errors'].items():
                    body += f"- {error_type}: {count}\n"
        
        body += "\nThis is an automated daily report from the Enterprise Chunker system."
        
        return self.send_email(self.config["admin_emails"], subject, body)
    
    def send_startup_notification(self, watch_folder, workers_count):
        """Send startup notification"""
        subject = "🚀 Chunker System Started"
        body = f"""
Enterprise Chunker System Started

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Watch Folder: {watch_folder}
Parallel Workers: {workers_count}
Database: Enabled
Notifications: {'Enabled' if self.config.get('enable_notifications') else 'Disabled'}

System is now monitoring for new files to process.
"""
        
        return self.send_email(self.config["admin_emails"], subject, body)
    
    def send_shutdown_notification(self, session_stats):
        """Send shutdown notification"""
        subject = "🛑 Chunker System Stopped"
        
        # Calculate uptime
        session_start = session_stats.get('session_start')
        uptime = "Unknown"
        if session_start:
            try:
                start_time = datetime.strptime(session_start, '%Y-%m-%d %H:%M:%S')
                uptime_delta = datetime.now() - start_time
                uptime = str(uptime_delta).split('.')[0]  # Remove microseconds
            except:
                pass
        
        body = f"""
Enterprise Chunker System Stopped

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {uptime}

Session Summary:
- Files Processed: {session_stats.get('files_processed', 0)}
- Chunks Created: {session_stats.get('chunks_created', 0)}
- Zero-byte Prevented: {session_stats.get('zero_byte_prevented', 0)}
- Errors: {session_stats.get('errors', 0)}
- Total Sentences: {session_stats.get('total_sentences_processed', 0)}
- Total Bytes: {session_stats.get('total_bytes_created', 0):,}

Department Breakdown:
"""
        
        for dept, stats in session_stats.get('department_breakdown', {}).items():
            body += f"- {dept}: {stats.get('files', 0)} files, {stats.get('chunks', 0)} chunks, {stats.get('errors', 0)} errors\n"
        
        body += "\nThis is an automated shutdown notification from the Enterprise Chunker system."
        
        return self.send_email(self.config["admin_emails"], subject, body)
