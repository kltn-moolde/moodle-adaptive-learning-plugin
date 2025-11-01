#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Configuration for Course Service
=========================================
Centralized logging setup with structured logs
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Reset levelname for other handlers
        record.levelname = levelname
        
        return result


def setup_logger(name: str = 'courseservice', level: str = 'INFO', log_dir: str = 'logs') -> logging.Logger:
    """
    Setup logger with console and file handlers
    
    Args:
        name: Logger name (module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Console handler (colored)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (all logs)
    file_handler = RotatingFileHandler(
        log_path / f'{name}.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Error file handler (only errors)
    error_handler = RotatingFileHandler(
        log_path / f'{name}_error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger


# Default logger for the service
logger = setup_logger()


def log_request(func):
    """Decorator to log API requests"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        logger.info(f"→ {request.method} {request.path}")
        logger.debug(f"  Headers: {dict(request.headers)}")
        
        # Safely get JSON body (don't raise error if no JSON)
        body = request.get_json(force=True, silent=True)
        if body:
            logger.debug(f"  Body: {body}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"✓ {request.method} {request.path} - Success")
            return result
        except Exception as e:
            logger.error(f"✗ {request.method} {request.path} - Error: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time"""
    from functools import wraps
    import time
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"⏱ Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"✓ {func.__name__} completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"✗ {func.__name__} failed after {elapsed:.3f}s: {str(e)}")
            raise
    
    return wrapper


if __name__ == '__main__':
    # Test logging
    test_logger = setup_logger('test', level='DEBUG')
    
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")
    
    print("\n✓ Logs written to logs/ directory")
