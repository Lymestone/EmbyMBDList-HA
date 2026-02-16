import threading
import collections
import time
import sys
import io


class LogTee(io.TextIOBase):
    """Tee stdout to both original stdout and a deque buffer."""

    def __init__(self, original, buffer, lock):
        self.original = original
        self.buffer = buffer
        self.lock = lock

    def write(self, s):
        self.original.write(s)
        if s.strip():
            with self.lock:
                self.buffer.append(s.rstrip())
        return len(s)

    def flush(self):
        self.original.flush()

    def fileno(self):
        return self.original.fileno()

    def isatty(self):
        return self.original.isatty()


class SyncManager:
    def __init__(self, config_path="config.cfg"):
        self.config_path = config_path
        self.status = "idle"
        self.last_sync_time = None
        self.next_sync_time = None
        self.last_summary = ""
        self.force_sync_event = threading.Event()
        self.config_lock = threading.Lock()
        self.log_lock = threading.Lock()
        self.log_buffer = collections.deque(maxlen=500)
        self.is_running = True

        # Install log tee
        sys.stdout = LogTee(sys.__stdout__, self.log_buffer, self.log_lock)

    def sync_loop(self):
        """Runs in a background thread. Performs sync cycles."""
        from app import init_from_config, run_single_sync

        while self.is_running:
            self.status = "syncing"
            hours = 6
            try:
                with self.config_lock:
                    ctx = init_from_config(self.config_path)
                hours = ctx.get("hours_between_refresh", 6)
                summary = run_single_sync(ctx)
                self.last_summary = summary
                self.last_sync_time = time.time()
            except Exception as e:
                self.status = "error"
                self.last_summary = f"Error: {e}"
                print(f"Sync error: {e}")

            if hours == 0:
                self.status = "stopped"
                break

            self.status = "waiting"
            self.next_sync_time = time.time() + (hours * 3600)
            print(f"\n\nWaiting {hours} hours for next refresh.\n\n")
            self._interruptible_sleep(hours * 3600)

    def _interruptible_sleep(self, seconds):
        """Sleep that can be interrupted by force_sync_event."""
        end_time = time.time() + seconds
        while time.time() < end_time and self.is_running:
            if self.force_sync_event.wait(timeout=5):
                self.force_sync_event.clear()
                break

    def trigger_force_sync(self):
        if self.status == "syncing":
            return False
        self.force_sync_event.set()
        return True

    def get_logs(self, count=200):
        with self.log_lock:
            return list(self.log_buffer)[-count:]

    def get_status_dict(self):
        return {
            "status": self.status,
            "last_sync_time": self.last_sync_time,
            "next_sync_time": self.next_sync_time,
            "last_summary": self.last_summary,
        }
