import logging
import math
import re
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from time import sleep

import argparse

from generate_maximum_projection import generate_maximum_projection_cli_str
from models.image_filename import *
from models.image_filename_glob import *
from models.paths import *
from models.swarm_job import SwarmJob, shard_job_params

FILES_PER_CALL_COUNT = 2000
MEMORY = 2

LOGGER = logging.getLogger()
class GenerateAllMaximumProjectionsJob:
  def __init__(self, source, destination, log):
    self.source = source
    self.destination = destination
    self.logdir = log
    self.logger = logging.getLogger()
  
  def run(self):
    SwarmJob(
      self.source,
      self.destination_path,
      self.job_name,
      self.file_dictionary,
      self.cli_str,
      self.logdir,
      MEMORY,
      FILES_PER_CALL_COUNT
    ).run()

    
  @property
  def cli_str(self):
    if not hasattr(self, "_cli_str"):
      self._cli_str = generate_maximum_projection_cli_str(
          self.source,
          self.destination)
    return self._cli_str

  @property
  def file_dictionary(self):
    if not hasattr(self, "_file_dictionary"):
      self._file_dictionary = self.destination_path / "input_file_dictionary.txt"
      LOGGER.warning("Generating file dictionary (this can take a while)")
      with self._file_dictionary.open("w") as file_dictionary:
        for position in self.distinct_image_filename_globs:
            file_dictionary.write("%s\n"%position)
    return self._file_dictionary

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
    return self.source_path.rglob(str(ImageFilenameGlob(suffix="", extension="tif")))


  @property
  def image_filenames(self):
    return (ImageFilename.parse(str(image_file_path.relative_to(self.source_path))) for image_file_path in self.image_file_paths)

  @property
  def distinct_image_filename_globs(self):
    if not hasattr(self, "_distinct_image_filename_globs"):
      self._distinct_image_filename_globs = set((
        ImageFilenameGlob.from_image_filename(image_filename, excluding_keys=["z"])
        for image_filename in self.image_filenames
      ))
    return self._distinct_image_filename_globs

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")

def generate_all_maximum_projections_cli(parser):
  args = parser.parse_args()
  try:
    GenerateAllMaximumProjectionsJob(
      args.source,
      args.destination
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
  generate_all_maximum_projections_cli(parser)
