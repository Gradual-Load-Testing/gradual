"""
Configuration file for pytest that sets up gevent monkey patching.
This ensures all tests run with proper gevent compatibility.
"""

# Monkey patch must happen before any other imports
import gevent.monkey
import sys

# Debug logging for monkey patching
print("Python version:", sys.version)
print("Gevent version:", gevent.__version__)

# Apply monkey patching with explicit modules
gevent.monkey.patch_all(
    socket=True,
    dns=True,
    time=True,
    select=True,
    thread=True,
    os=True,
    ssl=True,
    subprocess=True,
    sys=True,
    builtins=True,
    signal=True,
    queue=True,
    contextvars=True,
    _threading_local=True
)

# Now we can safely import other modules
import pytest
import logging
import socket
import threading
import time
import gevent

# Configure logging to prevent duplicate output
logging.basicConfig(level=logging.INFO)
# Remove any existing handlers to prevent duplicate logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
# Add a single handler
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logging.root.addHandler(handler)
logger = logging.getLogger(__name__)

class MonkeyPatchingError(Exception):
    """Raised when gevent monkey patching is not properly applied."""
    pass

def verify_monkey_patching():
    """Verify that gevent monkey patching has been applied correctly.
    
    Raises:
        MonkeyPatchingError: If any required module is not properly patched.
    """
    errors = []
    
    # Check if socket module is patched
    try:
        s = socket.socket()
        if not isinstance(s, gevent.socket.socket):
            errors.append("Socket module is not monkey patched!")
        else:
            logger.info("Socket module is monkey patched ✓")
    except Exception as e:
        errors.append(f"Socket module check failed: {e}")

    # Check if threading module is patched
    try:
        t = threading.Thread()
        if not isinstance(t, gevent.threading.Thread):
            errors.append("Threading module is not monkey patched!")
        else:
            logger.info("Threading module is monkey patched ✓")
    except Exception as e:
        errors.append(f"Threading module check failed: {e}")

    # Check if time module is patched
    try:
        if time.sleep is not gevent.sleep:
            errors.append("Time module is not monkey patched!")
        else:
            logger.info("Time module is monkey patched ✓")
    except Exception as e:
        errors.append(f"Time module check failed: {e}")

    if errors:
        error_msg = "\n".join(errors)
        logger.error(error_msg)
        raise MonkeyPatchingError(error_msg)

# Verify patching immediately
logger.info("Verifying initial monkey patching...")
verify_monkey_patching()

@pytest.fixture(autouse=True)
def verify_patching_before_test():
    """Verify monkey patching before each test.
    
    Raises:
        MonkeyPatchingError: If any required module is not properly patched.
    """
    verify_monkey_patching() 