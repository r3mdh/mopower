#!/usr/bin/python3

import sys, getopt

def write_with_lock (text, filename, mode):
  import signal, errno
  from contextlib import contextmanager
  import fcntl

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

  with timeout(25):
    try:
      f = open(filename, mode)
      fcntl.flock(f.fileno(), fcntl.LOCK_EX)
      print(text,file=f)
      f.flush()
      fcntl.flock(f.fileno(), fcntl.LOCK_UN)
      f.close()
      return 0    # Success
    except InterruptedError:
      # Catch the exception raised by the handler
      # If we weren't raising an exception, flock would automatically retry on signals
      return 1    # Failed to obtain lock

def main(argv):
  text = ''
  filename = ''
  mode = ''
  num_mandatory_args = 3
  
  try:
    opts, args = getopt.getopt(argv,"ht:f:m:",["text=","filename=","mode="])
  except getopt.GetoptError:
    print('write_with_lock.py -t <text> -f <filename> -m <mode>')
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', "--help"):
      print('write_with_lock.py -t <text> -f <filename> -m <mode=[w|a]>')
      print('write_with_lock.py --text <text> --filename <filename> --mode <mode=[w|a]>')
      sys.exit()
    elif opt in ("-t", "--text"):
      text = arg
    elif opt in ("-f", "--filename"):
      filename = arg
    elif opt in ("-m", "--mode"):
      mode = arg
  if len(sys.argv) < (num_mandatory_args * 2):     # Must include all mandatory arguments (+ corresponding options)
    print('write_with_lock.py -t <text> -f <filename> -m <mode>')  
    sys.exit(2)
  if (mode != "a") and (mode != "w"):
    print('Mode specified: ',mode)
    print('Valid mode: [w|a]')
    sys.exit(2)
  exitcode = write_with_lock(text,filename,mode)  
  if exitcode:
    print("Could not obtain lock")

  
if __name__ == "__main__":
  main(sys.argv[1:])
