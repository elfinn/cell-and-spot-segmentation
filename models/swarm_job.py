import logging
import math
import os
import shlex
import subprocess
import enum
from time import sleep

LOGGER = logging.getLogger()
MAX_ARGS_PER_JOB = 820

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
  file_type = "LSM" if os.environ.get('FILE_TYPE') == "LSM" else "IMX"
  user = os.environ.get('USER')

  def __init__(self, source, destination_path, name, file_dict, cli_str, logdir, mem, files_count):
    self.source = source
    self.destination_path = destination_path
    self.name = name
    self.file_dictionary = file_dict
    self.cli_str = cli_str
    self.mem = mem
    self.logdir = logdir
    self.files_per_call = min(files_count, MAX_ARGS_PER_JOB)

  def run(self):
    if self.run_strategy == RunStrategy.LOCAL:
      LOGGER.warning("running %s in development mode", self.name)
    else:
      LOGGER.warning("running %s in parallel mode", self.name)          
    self.generate_shell_file()
    self.start()

  def start(self):
    command = ["sbatch", "--wait",
               self.shell_file_path]
    LOGGER.warning(command)
    subprocess.run(command)
        
  def generate_shell_file(self):
    with self.shell_file_path.open("w") as shell_file:
      shell_file.write(self.shell_headers)
      shell_file.write("cat %s | parallel --verbose -j %s -N %s %s"%(self.file_dictionary,
                                                          self.jobs,
                                                          self.files_per_call,
                                                          self.cli_str))
        
  @property
  def shell_file_path(self):
    if not hasattr(self, "_shell_file_path"):
      self._shell_file_path = self.destination_path / ("%s.sh" % self.name)
    return self._shell_file_path

  @property
  def log_file_path(self):
    if not hasattr(self, "_log_file_path"):
      self._log_file_path = self.destination_path / ("slurm-%x.%A.%a.log")
    return self._log_file_path

  @property
  def shell_headers(self):
    if not hasattr(self, "_shell_headers"):
      self._shell_headers = "\n".join(["#!/bin/bash -l",
                                      "#SBATCH -A finn-lab",
                                      "#SBATCH --output %s"%self.log_file_path,
                                      "##SBATCH --mail-user %s@omrf.org"%self.user,
                                      "#SBATCH --mail-type END,FAIL,ARRAY_TASKS",
                                      "#SBATCH --mem 0",
                                      "#SBATCH -p serial",
                                      "#SBATCH --nodes 1",
                                      "#SBATCH --cpus-per-task 2",
                                      "#SBATCH -t 12:00:00", "",
                                      "set -eux",
                                      "export FILE_TYPE=\"%s\""%self.file_type, "",
                                      "module load slurm",
                                      "module load python/3.10.2",
                                      "module load numpy matplotlib scikit-learn cellpose",""])
    return self._shell_headers
    
  @property
  def export_string(self):
    if not hasattr(self, "_export_string"):
        self._export_string = '"\"--export=MKL_NUM_THREADS=2,FILE_TYPE=\"%s\"\""' % self.file_type
    return self._export_string

  @property
  def jobs(self):
    if not hasattr(self, "_jobs"):
      if self.run_strategy == RunStrategy.LOCAL:
        self._jobs = 1
      else:
        self._jobs = 16
    return self._jobs
