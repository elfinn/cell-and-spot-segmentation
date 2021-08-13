import cli.log
from datetime import datetime
import traceback
from pathlib import Path
import logging

from generate_nuclear_segmentation import generate_nuclear_segmentation_cli_str

from models.paths import *
from models.swarm_job import SwarmJob, shard_job_params
from models.image_filename_glob import ImageFilenameGlob

FILES_PER_CALL_COUNT = 10
MEMORY = 8

class GenerateAllNuclearSegmentationsJob:
  def __init__(self, source, destination, log, diameter, DAPI_channel=1):
    self.source = source
    self.destination = destination
    self.diameter = diameter
    self.logdir = log
    self.DAPI = DAPI_channel
    self.logger = logging.getLogger()

  def run(self):
    SwarmJob(
      self.source,
      self.destination_path,
      self.job_name,
      self.jobs,
      self.logdir,
      MEMORY,
      FILES_PER_CALL_COUNT
    ).run()

  @property
  def jobs(self):
    if not hasattr(self, "_jobs"):
      source_filenames_shards = shard_job_params(self.source_filenames, FILES_PER_CALL_COUNT)
      self._jobs = [
        generate_nuclear_segmentation_cli_str(source_filenames_shard, self.destination, self.source, self.diameter)
        for source_filenames_shard in source_filenames_shards
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
    return self.source_path.rglob(str(ImageFilenameGlob(c=self.DAPI, suffix="_maximum_projection", extension="tif")))

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
