import traceback
from datetime import datetime
import cli.log
import logging

from generate_spot_positions import generate_spot_positions_cli_str

from models.paths import *
from models.swarm_job import SwarmJob
from models.image_filename import ImageFilename

SWARM_SUBJOBS_COUNT = 5

class GenerateAllSpotPositionsJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination
    self.logger = logging.getLogger()

  def run(self):
    SwarmJob(
      self.destination_path,
      self.job_name,
      self.jobs,
      SWARM_SUBJOBS_COUNT
    ).run()

  @property
  def jobs(self):
    if not hasattr(self, "_jobs"):
      self._jobs = [
        generate_spot_positions_cli_str(
          nuclear_mask_path,
          self.destination,
          contrast_threshold=self.contrast_threshold_for_nuclear_mask_path(nuclear_mask_path)
        )
        for nuclear_mask_path
        in self.nuclear_mask_paths
      ]
    return self._jobs

  def contrast_threshold_for_nuclear_mask_path(self, nuclear_mask_path):
    c = ImageFilename(nuclear_mask_path.name).c
    if c == 3:
      return 4
    return None

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_maximum_projections_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
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
    return self.source_path.glob("*_cropped_???.npy")

@cli.log.LoggingApp
def generate_all_spot_positions_cli(app):
  try:
    GenerateAllSpotPositionsJob(
      app.params.source,
      app.params.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_spot_positions_cli.add_param("source")
generate_all_spot_positions_cli.add_param("destination")

if __name__ == "__main__":
   generate_all_spot_positions_cli.run()
