
import shlex
import logging
import re
import traceback
from pathlib import Path

import numpy
import skimage.exposure
import skimage.io
import argparse

from models.paths import *
from models.z_sliced_image import ZSlicedImage


class GenerateMaximumProjectionJob:
  def __init__(self, source_directory, filename_pattern, destination):
    self.source_directory = source_directory
    self.filename_pattern = filename_pattern
    self.destination = destination
    self.logger = logging.getLogger()

  def run(self):
    skimage.io.imsave(str(self.destination_path / self.maximum_projection_destination_filename), self.maximum_projection)
    numpy.save(str(self.destination_path / self.z_center_destination_filename), self.z_center)
    numpy.save(str(self.destination_path / self.summed_intensity_destination_filename), self.summed_intensity)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def source_directory_path(self):
    if not hasattr(self, "_source_directory_path"):
      self._source_directory_path = source_path(self.source_directory)
      if not self._source_directory_path.is_dir():
        raise Exception("image directory does not exist")
    return self._source_directory_path

  @property
  def source_file_paths(self):
    print("looking for source files with pattern %s"%self.filename_pattern)
    print("found %s"%next(self.source_directory_path.rglob(self.filename_pattern)))
    return self.source_directory_path.rglob(self.filename_pattern)

  @property
  def maximum_projection(self):
    if not hasattr(self, "_maximum_projection"):
      self.process_source_z_sliced_images()
    return self._maximum_projection

  @property
  def z_center(self):
    if not hasattr(self, "_z_center"):
      self.process_source_z_sliced_images()
    return self._z_center

  @property
  def summed_intensity(self):
    if not hasattr(self, "_summed_intensity"):
      self.process_source_z_sliced_images()
    return self._summed_intensity

  def process_source_z_sliced_images(self):
    if hasattr(self, "_z_center") or hasattr(self, "_maximum_projection"):
      raise Exception("already computed")

    first = next(self.source_z_sliced_images)
    maximum_projection = first.image
    summed_intensity = numpy.int32(first.image)
    weighted_summed_z_values = numpy.int32(first.image * first.z)
    
    for source_z_sliced_image in self.source_z_sliced_images:

      maximum_projection = numpy.fmax(maximum_projection, source_z_sliced_image.image)
      summed_intensity = summed_intensity + source_z_sliced_image.image
      weighted_summed_z_values = weighted_summed_z_values + (source_z_sliced_image.image * source_z_sliced_image.z)
        
    self._maximum_projection = maximum_projection
    self._summed_intensity = summed_intensity
    zero_adjusted_summed_intensity = summed_intensity
    zero_adjusted_summed_intensity[zero_adjusted_summed_intensity == 0] = 1
    zero_adjusted_weighted_summed_z_values = weighted_summed_z_values
    zero_adjusted_weighted_summed_z_values[zero_adjusted_weighted_summed_z_values == 0] = 1
    self._z_center = (zero_adjusted_weighted_summed_z_values / zero_adjusted_summed_intensity).astype(numpy.float16)

  @property
  def source_z_sliced_images(self):
    return (ZSlicedImage(source_file_path, self.source_directory_path) for source_file_path in self.source_file_paths)


  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      global_destination_path = Path(self.destination)
      local_destination_path = Path(self.filename_pattern).parents[0]
      self._destination_path = global_destination_path / local_destination_path
      if not self._destination_path.exists():
        Path.mkdir(self._destination_path, parents=True)
      elif not self._destination_path.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def destination_filename_prefix(self):
    return Path(self.filename_pattern.replace("?", "X").replace("*", "X")).stem
  
  @property
  def maximum_projection_destination_filename(self):
    return "%s%s" % (self.destination_filename_prefix, "_maximum_projection.tif")

  @property
  def z_center_destination_filename(self):
    return "%s%s" % (self.destination_filename_prefix, "_z_center")

  @property
  def summed_intensity_destination_filename(self):
    return "%s%s" % (self.destination_filename_prefix, "_summed_intensity")

def generate_maximum_projection_cli_str(source_directory, destination):
  return shlex.join([
    "python3",
    __file__,
    "--destination=%s" % destination,
    "--source_directory=%s" % source_directory
  ])

parser = argparse.ArgumentParser()
parser.add_argument("--source_directory", required=True)
parser.add_argument("--destination", required=True)
parser.add_argument("filename_patterns", nargs="*")

def generate_maximum_projection_cli(parser):
  args = parser.parse_args()
  for filename_pattern in args.filename_patterns:
    try:
      GenerateMaximumProjectionJob(
        args.source_directory,
        filename_pattern,
        args.destination
      ).run()
    except Exception as exception:
      traceback.print_exc()

if __name__ == "__main__":
   generate_maximum_projection_cli(parser)
