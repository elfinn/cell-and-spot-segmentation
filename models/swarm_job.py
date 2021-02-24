import logging
import math
import os
import shlex
import subprocess
from time import sleep

LOGGER = logging.getLogger()

def shard_job_params(job_params, shards_count):
  job_params_list = list(job_params)
  job_params_count = len(job_params_list)
  small_shard_job_params_count = math.floor(job_params_count / shards_count)
  large_shard_job_params_count = small_shard_job_params_count + 1
  large_shards_count = job_params_count % shards_count
  
  next_shard_start_index = 0
  for i in range(min(shards_count, job_params_count)):
    shard_jobs_count = large_shard_job_params_count if i < large_shards_count else small_shard_job_params_count
    shard_end_index = next_shard_start_index + shard_jobs_count
    yield job_params_list[next_shard_start_index:shard_end_index]
    next_shard_start_index = shard_end_index

class SwarmJob:
  def __init__(self, destination_path, name, jobs, parallelism):
    self.destination_path = destination_path
    self.name = name
    self.jobs = jobs
    self.parallelism = parallelism

  def run(self):
    if os.environ.get('ENVIRONMENT') == 'development':
      LOGGER.warning("running %s in development mode", self.name)
      for job in self.jobs:
        LOGGER.warning("command: %s", job)
        subprocess.run(shlex.split(job)).check_returncode()
      return
    self.generate_file()
    self.start()
    while not self.is_complete():
      LOGGER.warning("job not complete yet")
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
