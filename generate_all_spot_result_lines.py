import traceback
from datetime import datetime
import argparse
import logging

from generate_spot_result_line import generate_spot_result_line_cli_str

from models.paths import *
from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob
from models.swarm_job import SwarmJob, shard_job_params

FILES_PER_CALL_COUNT = 20000
MEMORY = 2

LOGGER = logging.getLogger()
class GenerateAllSpotResultLinesJob:
  def __init__(
    self,
    spots_source_directory,
    z_centers_source_directory,
    distance_transforms_source_directory,
    nuclear_masks_source_directory_path,
    destination,
    log
  ):
    self.spots_source_directory = spots_source_directory
    self.z_centers_source_directory = z_centers_source_directory
    self.distance_transforms_source_directory = distance_transforms_source_directory
    self.nuclear_masks_source_directory_path = nuclear_masks_source_directory_path
    self.destination = destination
    self.logdir = log
    self.logger = logging.getLogger()
  
  def run(self):
    SwarmJob(
      self.spots_source_directory,
      self.destination_path,
      self.job_name,
      self.file_dictionary,
      self.cli_str,
      self.logdir,
      MEMORY,
      FILES_PER_CALL_COUNT
    ).run()

  @property
  def file_dictionary(self):
    if not hasattr(self, "_file_dictionary"):
      self._file_dictionary = self.destination_path / "input_file_dictionary.txt"
      LOGGER.warning("Generating file dictionary (this can take a while)")
      with self._file_dictionary.open("w") as file_dictionary:
        for path in self.spot_source_paths:
          file_dictionary.write("%s\n"%path)
    return self._file_dictionary
    
  @property
  def cli_str(self):
    if not hasattr(self, "_cli_str"):
      self._cli_str = generate_spot_result_line_cli_str(
          self.spots_source_directory,
          self.z_centers_source_directory,
          self.distance_transforms_source_directory,
          self.nuclear_masks_source_directory_path,
          self.destination)
    return self._cli_str

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_spot_result_lines_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name
  
  @property
  def spots_source_directory_path(self):
    if not hasattr(self, "_spots_source_directory_path"):
      self._spots_source_directory_path = source_path(self.spots_source_directory)
      if not self._spots_source_directory_path.is_dir():
        raise Exception("spots source directory does not exist")
    return self._spots_source_directory_path

  @property
  def spot_source_paths(self):
    return self.spots_source_directory_path.rglob(str(ImageFilenameGlob(suffix="_nucleus_???_spot_*", extension="npy")))

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

parser = argparse.ArgumentParser()
parser.add_argument("spots_source_directory", default="todo", nargs="?")
parser.add_argument("z_centers_source_directory", default="todo", nargs="?")
parser.add_argument("distance_transforms_source_directory", default="todo", nargs="?")
parser.add_argument("nuclear_masks_source_directory_path", default="todo", nargs="?")
parser.add_argument("destination", default="\\hpc-prj\\finn\\data\\Results\\orphan_lines\\", nargs="?")

def generate_all_spot_result_lines_cli(parser):
  args = parser.parse_args()
  try:
    GenerateAllSpotResultLinesJob(
      args.spots_source_directory,
      args.z_centers_source_directory,
      args.distance_transforms_source_directory,
      args.nuclear_masks_source_directory_path,
      args.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
   generate_all_spot_result_lines_cli(parser)
