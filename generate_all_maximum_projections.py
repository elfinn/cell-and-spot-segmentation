import math
import traceback
from datetime import datetime
from pathlib import Path
import cli.log
import logging
from generate_maximum_projection import generate_maximum_projection_cli_str
import subprocess
from time import sleep
import re

from models.paths import *
from models.image_filename import *
from models.image_filename_glob import *
from models.swarm_job import SwarmJob

SWARM_SUBJOBS_COUNT = 5

class GenerateAllMaximumProjectionsJob:
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
        generate_maximum_projection_cli_str(self.source, image_filename_glob, self.destination) for image_filename_glob in self.distinct_image_filename_constraints
      ]
    return self._jobs

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
  def image_file_paths(self):
    return self.source_path.glob(str(ImageFilenameGlob(suffix="", extension="tif")))

  @property
  def image_filenames(self):
    return (ImageFilename(image_file_path.name) for image_file_path in self.image_file_paths)

  @property
  def distinct_image_filename_constraints(self):
    if not hasattr(self, "_distinct_image_filename_constraints"):
      self._distinct_image_filename_constraints = set((
        ImageFilenameGlob.from_image_filename(image_filename, excluding_keys=["z"]) for image_filename in self.image_filenames
      ))
    return self._distinct_image_filename_constraints

@cli.log.LoggingApp
def generate_all_maximum_projections_cli(app):
  try:
    GenerateAllMaximumProjectionsJob(
      app.params.source,
      app.params.destination
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_maximum_projections_cli.add_param("source")
generate_all_maximum_projections_cli.add_param("destination")

if __name__ == "__main__":
  generate_all_maximum_projections_cli.run()
