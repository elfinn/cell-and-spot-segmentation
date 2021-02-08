import cli.log
from datetime import datetime
import traceback
from pathlib import Path
import logging

from generate_nuclear_mask import generate_nuclear_mask_cli_str

from models.swarm_job import SwarmJob

SWARM_SUBJOBS_COUNT = 5

class GenerateAllNuclearMasksJob:
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
        generate_nuclear_mask_cli_str(source_filename, self.destination, self.diameter) for source_filename in self.source_filenames
      ]
    return self._jobs

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_nuclear_masks_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name    
  
  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = Path(self.source)
      if not self._source_path.is_dir():
        raise Exception("source does not exist")
    return self._source_path
  
  @property
  def source_filenames(self):
    return self.source_path.glob("*ZXXC01_maximum_projection.png")

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = Path(self.destination)
      if not self._destination_path.exists():
        Path.mkdir(self._destination_path, parents=True)
      elif not self._destination_path.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

@cli.log.LoggingApp
def generate_all_nuclear_masks(app):
  try:
    GenerateAllNuclearMasksJob(
      app.params.source,
      app.params.destination,
      app.params.diameter
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_nuclear_masks.add_param("source")
generate_all_nuclear_masks.add_param("destination")
generate_all_nuclear_masks.add_param("--diameter", type=int)

if __name__ == "__main__":
  generate_all_nuclear_masks.run()
