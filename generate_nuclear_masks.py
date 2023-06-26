import shlex
import traceback

import argparse
import numpy
import skimage.measure

from models.nuclear_mask import NuclearMask
from models.paths import *


class GenerateNuclearMasksJob:
  def __init__(self, source, destination, source_dir):
    self.source = source
    self.destination = destination
    self.source_dir = Path(source_dir)

  def run(self):
    for index, nuclear_mask in enumerate(self.nuclear_masks):
      numpy.save(self.indexed_destination_filename(index + 1), nuclear_mask)

  def indexed_destination_filename(self, index):
    source_relative_path = str(self.source_path.relative_to(self.source_dir))
    return self.destination_path / source_relative_path.replace("_nuc_seg", ("_nucleus_%03i" % index))

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

  @property
  def segmentation(self):
    if not hasattr(self, "_segmentation"):
      self._segmentation = numpy.load(self.source_path, allow_pickle=True)
    return self._segmentation

  @property
  def regionprops(self):
    if not hasattr(self, "_regionprops"):
      self._regionprops = skimage.measure.regionprops(self.segmentation)
    return self._regionprops

  @property
  def nuclear_masks(self):
    if not hasattr(self, "_nuclear_masks"):
      self._nuclear_masks = [
        NuclearMask.build(self.segmentation, rp) for rp in self.regionprops
      ]
    return self._nuclear_masks

def generate_nuclear_masks_cli_str(destination, source_dir):
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

def generate_nuclear_masks_cli(parser):
  args = parser.parse_args()
  for source in args.sources:
    try:
      GenerateNuclearMasksJob(
        source,
        args.destination,
        args.source_dir,
      ).run()
    except Exception as exception:
      traceback.print_exc()

if __name__ == "__main__":
   generate_nuclear_masks_cli(parser)
