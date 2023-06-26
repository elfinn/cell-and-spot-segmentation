import copy
import logging
import shlex
import traceback

import argparse
import numpy
from scipy import ndimage

from models.paths import *


class GenerateDistanceTransformJob:
  def __init__(self, source, destination, source_dir):
    self.source = source
    self.destination = destination
    self.source_dir = Path(source_dir)

  def run(self):
    numpy.save(self.destination_filename, self.distance_transform)

  @property
  def destination_filename(self):
    source_relative_path = str(self.source_path.relative_to(self.source_dir))
    return self.destination_path / source_relative_path.replace("_nucleus_", "_dt_")

  @property
  def distance_transform(self):
    if not hasattr(self, "_dt"):
       raw_transform = ndimage.distance_transform_edt(self.nuclear_mask)
       normed_transform = raw_transform/numpy.amax(raw_transform)
       self._distance_transform = 1 - normed_transform
    return self._distance_transform
  
  @property
  def nuclear_mask(self):
    if not hasattr(self, "_mask"):
      self._nuclear_mask = numpy.load(self.source_path, allow_pickle=True).item().mask
    return self._nuclear_mask

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      global_destination_path = Path(self.destination)
      local_destination_path = Path(str(self.source_path.relative_to(self.source_dir))).parents[0]
      path_to_make = global_destination_path / local_destination_path
      self._destination_path = global_destination_path 
      if not path_to_make.exists():
        Path.mkdir(path_to_make, parents=True)
      elif not path_to_make.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

def generate_distance_transform_cli_str(destination, source_dir):
  return shlex.join([
    "python3",
    __file__,
    "--destination=%s" % destination,
    "--source_dir=%s" % source_dir
  ])

parser = argparse.ArgumentParser()
parser.add_argument("sources", nargs="*")
parser.add_argument("--destination", required=True)
parser.add_argument("--source_dir", required=True)

def generate_distance_transform_cli(parser):
  args = parser.parse_args()
  for source in args.sources:
    try:
      GenerateDistanceTransformJob(
        source,
        args.destination,
        args.source_dir,
      ).run()
    except Exception as exception:
      traceback.print_exc()

if __name__ == "__main__":
   generate_distance_transform_cli(parser)
