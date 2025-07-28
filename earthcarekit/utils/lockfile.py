import functools
import os
import threading
import time
from logging import Logger
from typing import Any, Callable


def log_message(msg: str, logger: Logger | None, level: str = "info") -> None:
    """Logs a message either to a logger or to stdout.

    Args:
        msg (str): The message to log.
        logger (Logger | None): Logger instance to use. If None, prints to stdout.
        level (str): Logging level as a string ("info", "warning", "error", etc.).
    """
    if logger:
        log_func = getattr(logger, level, logger.info)
        log_func(msg)
    else:
        print(msg)


def is_heartbeat_stale(heartbeat_path: str | None, max_age_seconds: int) -> bool:
    """Checks whether the heartbeat file is stale, which indicates that the process is no longer running.

    Args:
        heartbeat_path (str | None): Path to the heartbeat file.
        max_age_seconds (int): Maximum allowed age in seconds before considering it stale.

    Returns:
        True if the heartbeat is missing or stale, False otherwise.
    """
    if not heartbeat_path or not os.path.exists(heartbeat_path):
        return True  # No heartbeat = assume stale
    last_update = os.path.getmtime(heartbeat_path)
    age = time.time() - last_update
    return age > max_age_seconds


def heartbeat_writer(
    heartbeat_path: str,
    heartbeat_interval_seconds: int,
    stop_event: threading.Event,
    logger: Logger | None,
) -> None:
    """Periodically updates the heartbeat file until stopped.

    Args:
        heartbeat_path (str): Path to the heartbeat file.
        heartbeat_interval_seconds (int): Interval in seconds between heartbeat updates.
        stop_event (threading.Event): Event used to signal stopping the heartbeat writer.
        logger (Logger | None): Logger instance to use. If None, prints to stdout.
    """
    update_interval_seconds = 1  # seconds
    elapsed = 0

    while not stop_event.is_set():
        if elapsed >= heartbeat_interval_seconds:
            try:
                with open(heartbeat_path, "w") as f:
                    f.write(str(time.time()))
            except Exception as e:
                log_message(f"Failed to update heartbeat: {e}", logger, "error")
            elapsed = 0

        time.sleep(update_interval_seconds)
        elapsed += update_interval_seconds


def with_lockfile(
    lockfile_path: str,
    logger: Logger | None = None,
    heartbeat_path: str | None = None,
    heartbeat_interval_seconds: int = 60,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that ensures only one instance of a script runs at a time,
    using a lock file and optional heartbeat file for stale lock detection.

    Args:
        lockfile_path (str): Path to the lock file.
        logger (Logger | None): Logger instance to use for logging. If None, prints to stdout.
        heartbeat_path (str | None): Optional path to a heartbeat file that indicates script liveness.
        heartbeat_interval_seconds (int): Interval in seconds for heartbeat updates and staleness detection.

    Returns:
        A decorator that wraps the target function with lockfile and heartbeat management.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Handle existing lock
            if os.path.exists(lockfile_path):
                max_heartbeat_interval_seconds = heartbeat_interval_seconds * 10
                if is_heartbeat_stale(heartbeat_path, max_heartbeat_interval_seconds):
                    log_message(
                        f"Stale lock detected (heartbeat older than {max_heartbeat_interval_seconds} seconds). Removing lock.",
                        logger,
                        "warning",
                    )
                    try:
                        os.remove(lockfile_path)
                    except Exception as e:
                        log_message(
                            f"Failed to remove stale lock: {e}", logger, "error"
                        )
                        return
                else:
                    log_message(
                        f"Script is already running (lock: {lockfile_path}, heartbeat is fresh). Exiting.",
                        logger,
                        "warning",
                    )
                    return

            # Create new lock
            try:
                open(lockfile_path, "w").close()
                log_message("Lock activated.", logger)
            except Exception as e:
                log_message(f"Failed to create lock file: {e}", logger, "error")
                return

            # Setup heartbeat
            heartbeat_thread: threading.Thread | None = None
            heartbeat_stop_event: threading.Event = threading.Event()

            if heartbeat_path:
                heartbeat_thread = threading.Thread(
                    target=heartbeat_writer,
                    args=(
                        heartbeat_path,
                        heartbeat_interval_seconds,
                        heartbeat_stop_event,
                        logger,
                    ),
                    daemon=True,
                )
                heartbeat_thread.start()

            try:
                return func(*args, **kwargs)
            finally:
                # Cleanup heartbeat
                if heartbeat_path:
                    heartbeat_stop_event.set()
                    if heartbeat_thread:
                        heartbeat_thread.join()
                    try:
                        os.remove(heartbeat_path)
                        log_message("Heartbeat deactivated.", logger)
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        log_message(f"Failed to remove heartbeat: {e}", logger, "error")

                # Cleanup lock
                try:
                    os.remove(lockfile_path)
                    log_message("Lock deactivated.", logger)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    log_message(f"Failed to remove lock file: {e}", logger, "error")

        return wrapper

    return decorator
