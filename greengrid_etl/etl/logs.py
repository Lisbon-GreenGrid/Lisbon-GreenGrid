# Import required libraries
import sys
import logging

# Initialize logger
def init_logger() -> None:
     """
    Initialize and configure a logger for the ETL pipeline.

    This function sets up a logger named 'gps-logger' with the following configuration:
    - Logging level: INFO
    - StreamHandler: logs messages to the console
    - Log message format: "timestamp | log level | message"
    - Prevents log messages from propagating to the root logger to avoid duplicates

    Usage:
        Call this function once at the start of your application to configure logging.

    Returns:
        None
    """
    log_level = logging.INFO
    logging.basicConfig(level=log_level)
    logger = logging.getLogger("gps-logger")
    c_handler = logging.StreamHandler()
    c_handler.setLevel(log_level)
    c_format = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    logger.propagate = False     # Prevent log messages from being propagated to the root logger


def die(msg: str) -> None:
    """
    Log an error message and terminate the program with a non-zero exit code.

    This function is intended for fatal errors where the program cannot continue. 
    It logs the provided message at the ERROR level and then exits the process.

    Args:
        msg (str): The error message to log before termination.

    Raises:
        SystemExit: Always raises SystemExit with status code 1.
    """
    logging.getLogger("gps-logger").error(f"{msg}")
    sys.exit(1)


def info(msg: str) -> None:
    """
    Logs an informational message using the logger.

    This function sends the provided message to the Python logging system
    at the INFO level, under the logger named 'gps-logger'. It is intended
    for general informational messages that do not indicate errors or warnings.

    Args:
        msg (str): The message string to log.

    Returns:
        None
        
    """
    logging.getLogger("gps-logger").info(f"{msg}")


def done(msg: str) -> None:
    """
    Logs a success message and terminates the program.

    This function logs the provided message using the logger
    at the INFO level, and then exits the Python process with a success
    status code (0).

    Args:
        msg (str): The message to log before exiting.

    Raises:
        SystemExit: Always raised to terminate the program with exit code 0.
    """
    logging.getLogger("gps-logger").info(f"{msg}")
    sys.exit(0)

