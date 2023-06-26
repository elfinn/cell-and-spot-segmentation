import logging
import traceback
from datetime import datetime

import argparse

from generate_nuclear_masks import generate_nuclear_masks_cli_str
from models.paths import *
from models.swarm_job import SwarmJob, shard_job_params

FILES_PER_CALL_COUNT = 5000
MEMORY = 1.5

LOGGER = logging.getLogger()
class GenerateAllNuclearMasksJob:
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
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_nuclear_masks_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name    

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
      if not self._source_path.is_dir():
        raise Exception("image directory does not exist")
    return self._source_path

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path
  
  @property
  def cli_str(self):
    if not hasattr(self, "_cli_str"):
      self._cli_str = generate_nuclear_masks_cli_str(self.destination, self.source)
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
  def source_filenames(self):
    return self.source_path.rglob("*_nuc_seg.npy")

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")

def generate_all_nuclear_masks(parser):
  args = parser.parse_args()
  try:
    GenerateAllNuclearMasksJob(
      args.source,
      args.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
  generate_all_nuclear_masks(parser)
