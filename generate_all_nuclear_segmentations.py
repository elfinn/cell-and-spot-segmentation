import cli.log
from datetime import datetime
import traceback
from pathlib import Path
import logging

from generate_nuclear_segmentation import generate_nuclear_segmentation_cli_str

from models.paths import *
from models.swarm_job import SwarmJob

SWARM_SUBJOBS_COUNT = 5

class GenerateAllNuclearSegmentationsJob:
  def __init__(self, source, destination, diameter):
    self.source = source
    self.destination = destination
    self.diameter = diameter
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
        generate_nuclear_segmentation_cli_str(source_filename, self.destination, self.diameter) for source_filename in self.source_filenames
      ]
    return self._jobs

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_nuclear_segmentations_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name    
  
  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
      if not self._source_path.is_dir():
        raise Exception("image directory does not exist")
    return self._source_path
  
  @property
  def source_filenames(self):
    return self.source_path.glob("*ZXXC01_maximum_projection.png")

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

@cli.log.LoggingApp
def generate_all_nuclear_segmentations(app):
  try:
    GenerateAllNuclearSegmentationsJob(
      app.params.source,
      app.params.destination,
      app.params.diameter
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_nuclear_segmentations.add_param("source")
generate_all_nuclear_segmentations.add_param("destination")
generate_all_nuclear_segmentations.add_param("--diameter", type=int)

if __name__ == "__main__":
  generate_all_nuclear_segmentations.run()
