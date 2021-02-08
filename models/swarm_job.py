import math
from time import sleep
import subprocess
import logging

LOGGER = logging.getLogger()

class SwarmJob:
  def __init__(self, destination_path, name, jobs, parallelism):
    self.destination_path = destination_path
    self.name = name
    self.jobs = jobs
    self.parallelism = parallelism

  def run(self):
    self.generate_file()
    self.start()
    while not self.is_complete():
      self.logger.warning("job not complete yet")
      sleep(5)

  def start(self):
    command = [
      "swarm",
      "--module", "python/3.8",
      "-f", self.swarm_file_path,
      "--job-name", self.name,
      "-b", str(math.ceil(len(self.jobs) / self.parallelism))
    ]
    LOGGER.warning(command)
    subprocess.run(command).check_returncode()

  def is_complete(self):
    command = ["squeue", "-n", self.name, "-o", "%T", "-t", "all", "-h"]
    LOGGER.warning(command)
    sjobs_result = subprocess.run(command, capture_output=True, text=True)
    sjobs_result.check_returncode()
    result_lines = sjobs_result.stdout.splitlines()
    LOGGER.warning("squeue result: %s", result_lines)
    return (
      len(result_lines) == self.parallelism and
      all((result_line == "COMPLETED" for result_line in result_lines))
    )

  def generate_file(self):
    with self.swarm_file_path.open("w") as swarm_file:
      for job in self.jobs:
        swarm_file.write("%s\n" % job)

  @property
  def swarm_file_path(self):
    if not hasattr(self, "_swarm_file_path"):
      self._swarm_file_path = self.destination_path / ("%s.swarm" % self.name)
    return self._swarm_file_path
