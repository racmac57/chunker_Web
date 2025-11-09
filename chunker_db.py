# chunker_db.py
# Database module for enterprise chunker tracking

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import threading
from contextlib import nullcontext

try:
    import portalocker  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    portalocker = None

log = logging.getLogger(__name__)

class ChunkerDatabase:
    def __init__(self, db_path="chunker_tracking.db", timeout=60.0):
        self.db_path = db_path
        self.timeout = timeout
        self._dept_stats_lock = threading.Lock()
        self.init_database()
        try:
            if not self.run_integrity_check():
                log.warning("Database integrity check reported an issue at startup.")
        except Exception:
            log.exception("Failed to execute integrity check during initialization.")

    def _conn(self):
        conn = sqlite3.connect(self.db_path, timeout=60)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
        except sqlite3.OperationalError as pragma_error:
            log.debug("PRAGMA setup warning: %s", pragma_error)
        return conn
    
    def get_connection(self):
        """Get database connection with timeout and retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = self._conn()
                return conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    logging.warning(f"Database locked, retrying in 1 second (attempt {attempt + 1})")
                    time.sleep(1)
                else:
                    raise
            except Exception as e:
                logging.error(f"Database connection failed: {e}")
                raise
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Processing history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    original_size INTEGER,
                    chunks_created INTEGER,
                    total_chunk_size INTEGER,
                    processing_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    department TEXT,
                    department_config TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Error log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_message TEXT,
                    stack_trace TEXT,
                    filename TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    active_processes INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Department statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS department_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    department TEXT NOT NULL,
                    files_processed INTEGER DEFAULT 0,
                    chunks_created INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    total_processing_time REAL DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    def log_processing(self, filename, original_size, chunks_created, total_chunk_size, 
                      processing_time, success, error_message=None, department="default", 
                      department_config=None):
        """Log file processing results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            dept_config_json = json.dumps(department_config) if department_config else None
            
            cursor.execute('''
                INSERT INTO processing_history 
                (filename, original_size, chunks_created, total_chunk_size, 
                 processing_time, success, error_message, department, department_config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (filename, original_size, chunks_created, total_chunk_size,
                 processing_time, success, error_message, department, dept_config_json))
            
            # Update department statistics
            self._update_department_stats(department, success, chunks_created, processing_time)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to log processing: {e}")
            if 'conn' in locals():
                try:
                    conn.close()
                except:
                    pass
    
    def log_error(self, error_type, error_message=None, stack_trace=None, filename=None):
        """Log error information with retry handling for locked databases"""
        retries = 6
        delay = 0.5

        treat_as_file_first = (
            stack_trace is None
            and filename is None
            and error_message is not None
            and isinstance(error_type, str)
            and Path(str(error_type)).suffix
        )

        if treat_as_file_first:
            file_name = str(error_type)
            error_name = "GenericError"
            message = str(error_message)
        else:
            file_name = filename
            error_name = error_type or "UnknownError"
            message = str(error_message or "")

        for attempt in range(retries):
            try:
                with self._conn() as conn:
                    conn.execute(
                        '''
                        INSERT INTO error_log (error_type, error_message, stack_trace, filename)
                        VALUES (?, ?, ?, ?)
                        ''',
                        (
                            error_name,
                            message[:2048],
                            stack_trace,
                            file_name,
                        ),
                    )
                    conn.commit()
                return
            except sqlite3.OperationalError as exc:
                if "locked" in str(exc).lower() and attempt < retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 5.0)
                    continue
                log.warning("log_error failed after %s tries: %s", attempt + 1, exc)
                return
            except Exception as exc:  # noqa: BLE001
                log.error("Failed to log error: %s", exc)
                return
    
    def run_integrity_check(self) -> bool:
        try:
            with self._conn() as conn:
                row = conn.execute("PRAGMA integrity_check").fetchone()
                return bool(row and row[0] == "ok")
        except Exception as e:
            log.error("Integrity check failed: %s", e)
            return False
    
    def log_system_metrics(self, cpu_percent, memory_percent, disk_percent, active_processes):
        """Log system performance metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics (cpu_percent, memory_percent, disk_percent, active_processes)
                VALUES (?, ?, ?, ?)
            ''', (cpu_percent, memory_percent, disk_percent, active_processes))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to log system metrics: {e}")
            if 'conn' in locals():
                try:
                    conn.close()
                except:
                    pass
    
    def _update_department_stats(self, department, success, chunks_created, processing_time):
        """Update department statistics with retry logic for database locks"""
        max_retries = 5  # Increased from 3 to 5
        retry_delay = 1.0  # Increased from 0.5 to 1.0 second
        lock_path = Path(f"{self.db_path}.dept.lock")
        if portalocker:
            try:
                lock_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        lock_ctx = portalocker.Lock(str(lock_path), timeout=15) if portalocker else nullcontext()

        with self._dept_stats_lock:
            with lock_ctx:
                for attempt in range(max_retries):
                    conn = None
                    try:
                        conn = self.get_connection()
                        cursor = conn.cursor()

                        # Check if department exists
                        cursor.execute('SELECT * FROM department_stats WHERE department = ?', (department,))
                        exists = cursor.fetchone()

                        if exists:
                            # Update existing record
                            if success:
                                cursor.execute('''
                                    UPDATE department_stats
                                    SET files_processed = files_processed + 1,
                                        chunks_created = chunks_created + ?,
                                        total_processing_time = total_processing_time + ?,
                                        last_updated = CURRENT_TIMESTAMP
                                    WHERE department = ?
                                ''', (chunks_created, processing_time, department))
                            else:
                                cursor.execute('''
                                    UPDATE department_stats
                                    SET errors = errors + 1,
                                        last_updated = CURRENT_TIMESTAMP
                                    WHERE department = ?
                                ''', (department,))
                        else:
                            # Create new record
                            if success:
                                cursor.execute('''
                                    INSERT INTO department_stats
                                    (department, files_processed, chunks_created, total_processing_time)
                                    VALUES (?, 1, ?, ?)
                                ''', (department, chunks_created, processing_time))
                            else:
                                cursor.execute('''
                                    INSERT INTO department_stats
                                    (department, errors)
                                    VALUES (?, 1)
                                ''', (department,))

                        conn.commit()
                        conn.close()
                        return  # Success, exit retry loop

                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e) and attempt < max_retries - 1:
                            # Only log warning on first and last retry to reduce log spam
                            if attempt == 0 or attempt == max_retries - 2:
                                logging.warning(f"Department stats update locked, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                            if conn:
                                try:
                                    conn.close()
                                except:
                                    pass
                            time.sleep(retry_delay)
                            retry_delay *= 1.5  # Slower exponential backoff (was 2)
                        else:
                            logging.error(f"Failed to update department stats after {max_retries} attempts: {e}")
                            if conn:
                                try:
                                    conn.close()
                                except:
                                    pass
                    except Exception as e:
                        logging.error(f"Failed to update department stats: {e}")
                        if conn:
                            try:
                                conn.close()
                            except:
                                pass
                        break  # Don't retry on non-lock errors
    
    def get_analytics(self, days=1):
        """Get analytics for the specified number of days"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Processing statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_files,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_files,
                    SUM(chunks_created) as total_chunks,
                    AVG(processing_time) as avg_processing_time,
                    SUM(total_chunk_size) as total_bytes
                FROM processing_history 
                WHERE timestamp >= ?
            ''', (start_date.isoformat(),))
            
            processing_stats = cursor.fetchone()
            
            # Error statistics
            cursor.execute('''
                SELECT error_type, COUNT(*) as count
                FROM error_log 
                WHERE timestamp >= ?
                GROUP BY error_type
                ORDER BY count DESC
            ''', (start_date.isoformat(),))
            
            error_stats = cursor.fetchall()
            
            # Department breakdown
            cursor.execute('''
                SELECT department, files_processed, chunks_created, errors
                FROM department_stats
                WHERE last_updated >= ?
            ''', (start_date.isoformat(),))
            
            department_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                'processing': {
                    'total_files': processing_stats[0] or 0,
                    'successful_files': processing_stats[1] or 0,
                    'total_chunks': processing_stats[2] or 0,
                    'avg_processing_time': processing_stats[3] or 0,
                    'total_bytes': processing_stats[4] or 0
                },
                'errors': dict(error_stats),
                'departments': dict(department_stats)
            }
            
        except Exception as e:
            logging.error(f"Failed to get analytics: {e}")
            if 'conn' in locals():
                try:
                    conn.close()
                except:
                    pass
            return {}
    
    def cleanup_old_data(self, days=30):
        """Clean up old data from database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean up old processing history
            cursor.execute('DELETE FROM processing_history WHERE timestamp < ?', 
                         (cutoff_date.isoformat(),))
            
            # Clean up old error logs
            cursor.execute('DELETE FROM error_log WHERE timestamp < ?', 
                         (cutoff_date.isoformat(),))
            
            # Clean up old system metrics
            cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', 
                         (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logging.error(f"Failed to cleanup old data: {e}")
            if 'conn' in locals():
                try:
                    conn.close()
                except:
                    pass
