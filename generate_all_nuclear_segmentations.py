import argparse
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

LOGGER = logging.getLogger()
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
      self.file_dictionary,
      self.cli_str,
      self.logdir,
      MEMORY,
      FILES_PER_CALL_COUNT
    ).run()

    
  @property
  def cli_str(self):
    if not hasattr(self, "_cli_str"):
      self._cli_str = generate_nuclear_segmentation_cli_str(self.destination, self.source, self.diameter)
    return self._cli_str

  @property
  def file_dictionary(self):
    if not hasattr(self, "_file_dictionary"):
      self._file_dictionary = self.destination_path / "input_file_dictionary.txt"
      LOGGER.warning("Generating file dictionary (this can take a while)")
      with self._file_dictionary.open("w") as file_dictionary:
        for file in self.source_filenames:
            file_dictionary.write("%s\n"%file)
    return self._file_dictionary

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

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
parser.add_argument("--diameter", type=int)

def generate_all_nuclear_segmentations(parser):
  args = parser.parse_args()
  try:
    GenerateAllNuclearSegmentationsJob(
      args.source,
      args.destination,
      args.diameter
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
  generate_all_nuclear_segmentations(parser)
