#!/usr/bin/python3

import sys,getopt

def write_with_lock (text, filename, mode):
  import signal, errno
  from contextlib import contextmanager
  import fcntl
  import os.path
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

  with timeout(15):
    try:
      f = open(filename, mode)
      fcntl.flock(f.fileno(), fcntl.LOCK_EX)
      print(text,file=f)
      f.flush()     # Force a write

      # Now we wait for the UPS to store the results of the command in the filename.out file
      while not os.path.exists(filename + ".out"):
        time.sleep(0.1)
      
      with open(filename + ".out") as fr:
        lines=fr.readlines()

      lines = "".join(lines).strip()

      # Remove filename.out
      os.remove(filename + ".out")

      fcntl.flock(f.fileno(), fcntl.LOCK_UN)
      f.close()
      return lines
    except InterruptedError:
      # Catch the exception raised by the handler
      # If we weren't raising an exception, flock would automatically retry on signals
      return "Couldn't get a lock on " + filename


def main(argv):
  command = " ".join(sys.argv[1:]).strip()

  if command == "":
    helptext = """Must include command
COMMAND       DESCRIPTION
show all      Prints all common settings
show time     Prints all common time settings
show ups      Prints all common UPS settings
show data     Prints selected data variables w/CRC check
EEPROM RESET  Resets all common EEPROM variables
EEPROM SAVE   Saves all common settings to EEPROM
UPS-REBOOT    Reboots UPS"""
    print(helptext)
    sys.exit(1)
  else:
#    output = write_with_lock(command,"/run/shm/mopower/COMMAND","w")
    output = write_with_lock(command,"./COMMAND","w")
    print(output)
    
if __name__ == "__main__":
  main(sys.argv[1:])