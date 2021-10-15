import signal, errno
from contextlib import contextmanager
import fcntl
import time

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        # Now that flock retries automatically when interrupted, we need
        # an exception to stop it
        # This exception will propagate on the main thread, make sure you're calling flock there
        raise InterruptedError

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)

    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

with timeout(1):
    f = open("/root/test.txt", "w")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        print("Got lock")
    except InterruptedError:
        # Catch the exception raised by the handler
        # If we weren't raising an exception, flock would automatically retry on signals
        print("Lock timed out")
