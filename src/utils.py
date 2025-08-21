import os
import logging
from typing import List, Tuple
import shutil

def check_disk_usage(paths: List[str], threshold: int, logger: logging.Logger = None) -> List[Tuple[str, float]]:
    """
    Check disk usage for given paths and return paths that exceed threshold.

    Args:
        paths: List of paths to check
        threshold: Usage threshold percentage (0-100)
        logger: Optional logger for warnings

    Returns:
        List of tuples (path, usage_percentage) for paths exceeding threshold
    """
    if not 0 < threshold < 100:
        raise ValueError("Threshold must be between 1-99")

    if logger is None:
        logger = logging.getLogger(__name__)

    exceeding_paths = []

    for path in paths:
        try:
            # Get the directory of the path (in case it's a file)
            dir_path = os.path.dirname(path) if not os.path.isdir(path) else path

            # If directory doesn't exist, get parent directory
            while not os.path.exists(dir_path) and dir_path != '/':
                dir_path = os.path.dirname(dir_path)

            if dir_path == '/':
                logger.warning(f"Could not find valid directory for path checking: {path}")
                continue

            # Get disk usage statistics
            total, used, free = shutil.disk_usage(dir_path)
            usage_percent = (used / total) * 100

            if usage_percent > threshold:
                exceeding_paths.append((path, usage_percent))
                logger.warning(f"Disk usage for {dir_path}: {usage_percent:.1f}% exceeds threshold {threshold}%")
            else:
                logger.debug(f"Disk usage for {dir_path}: {usage_percent:.1f}% is within acceptable limits")

        except Exception as e:
            logger.error(f"Failed to check disk usage for {path}: {str(e)}")

    return exceeding_paths
