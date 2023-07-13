import re
import shlex
import traceback
from copy import copy
from functools import lru_cache

import argparse
import matplotlib.pyplot as plt
import numpy
import skimage.io
import skimage.measure
import skimage.util

from models.image_filename import ImageFilename
from models.nuclear_mask import NuclearMask
from models.paths import *


@lru_cache(maxsize=1)
def load_source_image(source_image_path):
  if source_image_path.suffix == ".tif":
    return skimage.io.imread(source_image_path)
  else:
    return numpy.load(source_image_path, allow_pickle=True)

class GenerateCroppedCellImageJob:
  def __init__(self, source_image, source_mask, destination, source_image_dir, source_mask_dir):
    self.source_image = source_image
    self.source_mask = source_mask
    self.destination = destination
    self.source_image_dir = Path(source_image_dir)
    self.source_mask_dir = Path(source_mask_dir)

  def run(self):
    numpy.save(self.destination_filename, self.masked_cropped_image)

  @property
  def destination_filename(self):
    return self.destination_path / str(self.destination_image_filename)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      global_destination_path = Path(self.destination)
      local_destination_path = Path(str(self.source_image_path.relative_to(self.source_image_dir))).parents[0]
      path_to_make = global_destination_path / local_destination_path
      self._destination_path = global_destination_path 
      if not path_to_make.exists():
        Path.mkdir(path_to_make, parents=True)
      elif not path_to_make.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def destination_image_filename(self):
    if not hasattr(self, "_destination_image_filename"):
      self._destination_image_filename = copy(self.source_image_filename)
      self._destination_image_filename.suffix = self.destination_suffix
      self._destination_image_filename.extension = "npy"
    return self._destination_image_filename

  @property
  def source_image_path(self):
    if not hasattr(self, "_source_image_path"):
      self._source_image_path = source_path(self.source_image)
    return self._source_image_path

  @property
  def source_mask_path(self):
    if not hasattr(self, "_source_mask_path"):
      self._source_mask_path = source_path(self.source_mask)
    return self._source_mask_path

  @property
  def source_image_filename(self):
    if not hasattr(self, "_source_image_filename"):
      self._source_image_filename = ImageFilename.parse(str(self.source_image_path.relative_to(self.source_image_dir)))
    return self._source_image_filename

  @property
  def source_image_suffix(self):
    return self.source_image_filename.suffix

  @property
  def source_mask_suffix(self):
    if not hasattr(self, "_source_mask_suffix"):
      self._source_mask_suffix = ImageFilename.parse(str(self.source_mask_path.relative_to(self.source_mask_dir))).suffix
    return self._source_mask_suffix

  @property
  def destination_suffix(self):
    if not hasattr(self, "_destination_suffix"):
        self._destination_suffix = self.source_image_suffix + self.source_mask_suffix
    return self._destination_suffix

  @property
  def mask(self):
    if not hasattr(self, "_mask"):
      self._mask = numpy.load(self.source_mask_path, allow_pickle=True).item()
    return self._mask

  @property
  def nuclear_mask(self):
    return self.mask.mask

  @property
  def nuclear_offset(self):
    return self.mask.offset

  @property
  def image(self):
      if not hasattr(self, "_image"):
        self._image = load_source_image(self.source_image_path)
      return self._image

  @property
  def rect_cropped_image(self):
    if not hasattr(self, "_rect_cropped_image"):
        [min_row, min_column] = self.nuclear_offset
        [rows_count, columns_count] = numpy.shape(self.nuclear_mask)
        self._rect_cropped_image = self.image[min_row:(min_row + rows_count), min_column:(min_column + columns_count)]
    return self._rect_cropped_image

  @property
  def min_in_nucleus(self):
    if not hasattr(self, "_min_in_nucleus"):
      self._min_in_nucleus = numpy.amin(self.rect_cropped_image, where=self.nuclear_mask, initial=100000)
    return self._min_in_nucleus

  @property
  def max_in_nucleus(self):
    if not hasattr(self, "_max_in_nucleus"):
      self._max_in_nucleus = numpy.amax(self.rect_cropped_image, where=self.nuclear_mask, initial=0)
    return self._max_in_nucleus

  @property
  def masked_cropped_image(self):
    if not hasattr(self, "_masked_cropped_image"):
      if self.source_image_filename.extension == "tif":
        normed_image = skimage.exposure.rescale_intensity(self.rect_cropped_image, in_range=(self.min_in_nucleus, self.max_in_nucleus), out_range=(0,1))
        self._masked_cropped_image = normed_image * self.nuclear_mask
      else:
        self._masked_cropped_image = self.rect_cropped_image * self.nuclear_mask
    return self._masked_cropped_image

def generate_cropped_cell_image_cli_str(destination, source_images_dir, source_masks_dir):
  return shlex.join([
    "python3",
    __file__,
    "--destination=%s" % destination,
    "--source_images_dir=%s" % source_images_dir,
    "--source_masks_dir=%s" % source_masks_dir,
  ])

parser = argparse.ArgumentParser()
parser.add_argument("serialized_files", nargs="*")
parser.add_argument("--destination", required=True)
parser.add_argument("--source_images_dir", required=True)
parser.add_argument("--source_masks_dir", required=True)

def generate_cropped_cell_image_cli(parser):
  args = parser.parse_args()
  for mask_pair in args.serialized_files:
    source_image, source_mask = mask_pair.split(';')
    try:
      GenerateCroppedCellImageJob(
        source_image,
        source_mask,
        args.destination,
        args.source_images_dir,
        args.source_masks_dir,
      ).run()
    except Exception as exception:
      traceback.print_exc()

if __name__ == "__main__":
   generate_cropped_cell_image_cli(parser)
