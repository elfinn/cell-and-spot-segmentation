import traceback
from datetime import datetime
import cli.log
import logging

from generate_distance_transform import generate_distance_transform_cli_str

from models.paths import *
from models.swarm_job import SwarmJob, shard_job_params

SWARM_SUBJOBS_COUNT = 20
MEMORY = 2

class GenerateAllDistanceTransformsJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination
    self.logger = logging.getLogger()

  def run(self):
    SwarmJob(
      self.destination_path,
      self.job_name,
      self.jobs,
      SWARM_SUBJOBS_COUNT,
      MEMORY
    ).run()

  @property
  def jobs(self):
    if not hasattr(self, "_jobs"):
      shards = shard_job_params(self.nuclear_mask_paths, SWARM_SUBJOBS_COUNT)
      self._jobs = [
        generate_distance_transform_cli_str(shard, self.destination) for shard in shards
      ]
    return self._jobs

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_distance_transforms_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name
  
  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path
  
  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path
  
  @property
  def nuclear_mask_paths(self):
    return self.source_path.glob("*_nuclear_mask_???.npy")

@cli.log.LoggingApp
def generate_all_distance_transforms_cli(app):
  try:
    GenerateAllDistanceTransformsJob(
      app.params.source,
      app.params.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_distance_transforms_cli.add_param("source")
generate_all_distance_transforms_cli.add_param("destination")

if __name__ == "__main__":
   generate_all_distance_transforms_cli.run()
