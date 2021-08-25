import traceback
from datetime import datetime
import cli.log
import logging

from generate_spot_positions import generate_spot_positions_cli_str

from models.paths import *
from models.swarm_job import SwarmJob, shard_job_params
from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob

FILES_PER_CALL = 20000
MEMORY = 2

class GenerateAllSpotPositionsJob:
  def __init__(self, source, destination, log, config=None):
    self.source = source
    self.destination = destination
    self.config = config
    self.logdir = log
    self.logger = logging.getLogger()

  def run(self):
    SwarmJob(
      self.source,
      self.destination_path,
      self.job_name,
      self.jobs,
      self.logdir,
      MEMORY,
      FILES_PER_CALL
    ).run()

  @property
  def jobs(self):
    if not hasattr(self, "_jobs"):
      nuclear_mask_paths_shards = shard_job_params(self.nuclear_mask_paths, FILES_PER_CALL)
      self._jobs = [
        generate_spot_positions_cli_str(nuclear_mask_paths_shard, self.destination, self.source, config=self.config)
        for nuclear_mask_paths_shard in nuclear_mask_paths_shards
      ]
    return self._jobs

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_spot_positions_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
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
    return self.source_path.rglob(str(ImageFilenameGlob(suffix="_maximum_projection_nuclear_mask_???", extension="npy")))

@cli.log.LoggingApp
def generate_all_spot_positions_cli(app):
  try:
    GenerateAllSpotPositionsJob(
      app.params.source,
      app.params.destination,
      app.params.source_dir,
      config=app.params.config
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_spot_positions_cli.add_param("source")
generate_all_spot_positions_cli.add_param("destination")
generate_all_spot_positions_cli.add_param("source_dir")
generate_all_spot_positions_cli.add_param("--config")

if __name__ == "__main__":
   generate_all_spot_positions_cli.run()
