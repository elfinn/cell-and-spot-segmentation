from time import sleep
import math
import subprocess
import logging

class SwarmJob:
  def __init__(self, filename, name, bundle=None):
    self.filename = filename
    self.name = name
    self.bundle = bundle
    self.logger = logging.getLogger()
  
  def run(self):
    self.start()
    while not self.is_complete():
      self.logger.warning("job not complete yet")
      sleep(5)
    self.logger.warning("complete")

  def start(self):
    command = ["swarm", "--module", "python/3.8", "-f", self.filename, "--job-name", self.name]
    if self.bundle:
      command = command + ["-b", str(self.bundle)]
    self.logger.warning(command)
    subprocess.run(command).check_returncode()

  def is_complete(self):
    command = ["squeue", "-n", self.name, "-o", "\"%T\"", "-t", "all", "-h"]
    sjobs_result = subprocess.run(command, capture_output=True, text=True)
    self.logger.warning(command)
    sjobs_result.check_returncode()
    result_lines = sjobs_result.stdout.splitlines()
    self.logger.warning("squeue result: %s", sjobs_result.stdout)
    return (
      len(result_lines) == len(self.distinct_image_filename_constraints) and
      all((result_line == "COMPLETED" for result_line in result_lines))
    )

