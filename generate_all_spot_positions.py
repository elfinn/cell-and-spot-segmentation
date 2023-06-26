import traceback
from datetime import datetime
import argparse
import logging

from generate_spot_positions import generate_spot_positions_cli_str

from models.paths import *
from models.swarm_job import SwarmJob, shard_job_params
from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob

FILES_PER_CALL = 20000
MEMORY = 2

LOGGER = logging.getLogger()
class GenerateAllSpotPositionsJob:
  def __init__(self, source, destination, log, DAPI, config=None):
    self.source = source
    self.destination = destination
    self.DAPI_channel = DAPI
    self.config = config
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
      FILES_PER_CALL
    ).run()

  @property
  def cli_str(self):
    if not hasattr(self, "_cli_str"):
      self._cli_str = generate_spot_positions_cli_str(self.destination, self.source, config=self.config)
    return self._cli_str

  @property
  def file_dictionary(self):
    if not hasattr(self, "_file_dictionary"):
      self._file_dictionary = self.destination_path / "input_file_dictionary.txt"
      LOGGER.warning("Generating file dictionary (this can take a while)")
      with self._file_dictionary.open("w") as file_dictionary:
        for mask in self.nuclear_mask_paths:
          file_dictionary.write("%s\n"%mask)
    return self._file_dictionary

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
    if not hasattr(self, "_nuclear_mask_paths"):
        self._nuclear_mask_paths = [
            image_file_path
            for image_file_path
            in self.source_path.rglob(str(ImageFilenameGlob(suffix="_maximum_projection_nucleus_???", extension="npy")))
            if ImageFilename.parse(str(image_file_path.relative_to(self.source_path))).c != self.DAPI_channel
          ]
    return self._nuclear_mask_paths

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
parser.add_argument("source_dir")
parser.add_argument("DAPI_channel")
parser.add_argument("--config")

def generate_all_spot_positions_cli(app):
  args = parser.parse_args()
  try:
    GenerateAllSpotPositionsJob(
      args.source,
      args.destination,
      args.source_dir,
      args.DAPI_channel,
      config=args.config
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
   generate_all_spot_positions_cli(parser)
