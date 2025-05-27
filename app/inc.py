
import os

def fetch_inc():
    """
    Fetches the increment value from the environment variable.
    Returns:
        int: The increment value.
    """
    try:
        inc = int(os.environ.get("INCREMENT", 1))
    except ValueError:
        inc = 1
    return inc
