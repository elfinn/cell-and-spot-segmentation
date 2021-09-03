import logging
import math
import os
import shlex
import subprocess
import enum
from time import sleep

LOGGER = logging.getLogger()
MAX_ARGS_PER_JOB = 10000

def shard_job_params(job_params, files_count):
  job_params_list = list(job_params)
  job_params_count = len(job_params_list)
  params_per_job = min(files_count, MAX_ARGS_PER_JOB)
  shards_count_sanitized = math.ceil(job_params_count/params_per_job)
  small_shard_job_params_count = math.floor(job_params_count / shards_count_sanitized)
  large_shard_job_params_count = small_shard_job_params_count + 1
  large_shards_count = job_params_count % shards_count_sanitized

  next_shard_start_index = 0
  for i in range(min(shards_count_sanitized, job_params_count)):
    shard_jobs_count = large_shard_job_params_count if i < large_shards_count else small_shard_job_params_count
    shard_end_index = next_shard_start_index + shard_jobs_count
    yield job_params_list[next_shard_start_index:shard_end_index]
    next_shard_start_index = shard_end_index

class RunStrategy(enum.Enum):
  LOCAL = enum.auto()
  SWARM = enum.auto()



class SwarmJob:
  run_strategy = RunStrategy.SWARM if os.environ.get('ENVIRONMENT') == 'production' else RunStrategy.LOCAL
  file_type = "LSM" if os.environ.get('FILE_TYPE') == "LSM" else "CV"
    
  def __init__(self, source, destination_path, name, jobs, logdir, mem, files_count):
    self.source = source
    self.destination_path = destination_path
    self.name = name
    self.jobs = jobs
    self.mem = mem
    self.logdir = logdir
    self.bundling = math.ceil(files_count/MAX_ARGS_PER_JOB)

  def run(self):
    if self.run_strategy == RunStrategy.LOCAL:
      LOGGER.warning("running %s in development mode", self.name)
      for job in self.jobs:
        LOGGER.warning("command: %s", job)
        subprocess.run(shlex.split(job)).check_returncode()
      return
    self.generate_file()
    self.start()
    while not self.is_complete():
      LOGGER.warning("job not complete yet")
      sleep(20)

  def start(self):
    command = [
      "swarm",
      "--module", "python/3.8",
      "-f", self.swarm_file_path,
      "--job-name", self.name,
      "-g", str(self.mem),
      "--logdir", str(self.logdir),
      "-b", str(self.bundling),
      "--sbatch", self.export_string
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
    if(any((result_line == "FAILED" for result_line in result_lines))):
        return True
    else: 
        return all((result_line == "COMPLETED" for result_line in result_lines))

  def generate_file(self):
    with self.swarm_file_path.open("w") as swarm_file:
      for job in self.jobs:
        swarm_file.write("%s\n" % job)

  @property
  def swarm_file_path(self):
    if not hasattr(self, "_swarm_file_path"):
      self._swarm_file_path = self.destination_path / ("%s.swarm" % self.name)
    return self._swarm_file_path

  @property
  def export_string(self):
    if not hasattr(self, "_export_string"):
        self._export_string = '"\"--export=MKL_NUM_THREADS=2,FILE_TYPE=\"%s\"\""' % self.file_type
    return self._export_string
