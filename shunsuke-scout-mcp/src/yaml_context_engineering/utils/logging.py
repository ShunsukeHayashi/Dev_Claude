"""Logging configuration for YAML Context Engineering."""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog
from structlog.stdlib import LoggerFactory
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    structured: bool = True
) -> None:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        structured: Whether to use structured logging
    """
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([] if not log_file else [logging.FileHandler(log_file)])
        ]
    )
    
    if structured:
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer(colors=True) if sys.stdout.isatty() else structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class ColoredLogger:
    """Simple colored logger for console output."""
    
    @staticmethod
    def info(msg: str) -> None:
        """Log info message in blue."""
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")
    
    @staticmethod
    def success(msg: str) -> None:
        """Log success message in green."""
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {msg}")
    
    @staticmethod
    def warning(msg: str) -> None:
        """Log warning message in yellow."""
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}")
    
    @staticmethod
    def error(msg: str) -> None:
        """Log error message in red."""
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")
    
    @staticmethod
    def debug(msg: str) -> None:
        """Log debug message in cyan."""
        print(f"{Fore.CYAN}[DEBUG]{Style.RESET_ALL} {msg}")


# Create a default colored logger instance
console = ColoredLogger()