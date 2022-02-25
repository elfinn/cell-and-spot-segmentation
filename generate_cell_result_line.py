import shlex
import csv
import logging
import re
import traceback
from copy import copy
from pathlib import Path
from functools import lru_cache

import cli.log
import numpy

from models.image_filename import ImageFilename
from models.paths import *

CELL_RESULT_FILE_SUFFIX_RE = re.compile("_nuclear_mask_(?P<nucleus_index>\d{3})")


@lru_cache(maxsize=1)
def load_source_image(source_image_path):
  if source_image_path.suffix == ".tif":
    return skimage.io.imread(source_image_path)
  else:
    return numpy.load(source_image_path, allow_pickle=True)


class GenerateCellResultLineJob:
  def __init__(self, source_image, source_mask, destination, source_image_dir, source_mask_dir):
    self.source_image = source_image
    self.source_mask = source_mask
    self.destination = destination
    self.source_image_dir = Path(source_image_dir)
    self.source_mask_dir = Path(source_mask_dir)
  
  def run(self):
    with open(self.destination_filename, 'w') as csv_file:
      csv_writer = csv.DictWriter(csv_file, self.csv_values.keys())
      csv_writer.writeheader()
      csv_writer.writerow(self.csv_values)

  @property
  def csv_values(self):
    return {
      "filename": str(self.source_image_filename),
      "experiment": self.source_image_filename.experiment,
      "well": self.source_image_filename.well,
      "field": self.source_image_filename.f,
      "channel": self.source_image_filename.c,
      "nucleus_index": self.nucleus_index,
      "area": self.area,
      "summed_intensity": self.summed_intensity
    }

  @property
  def destination_filename(self):
    return self.destination_path / str(self.destination_line_filename)

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
  def destination_line_filename(self):
    if not hasattr(self, "_destination_line_filename"):
      self._destination_line_filename = copy(self.source_image_filename)
      self._destination_line_filename.suffix = self.destination_suffix
      self._destination_line_filename.extension = "csv"
    return self._destination_line_filename

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
  def source_mask_filename(self):
    if not hasattr(self, "_source_mask_filename"):
      self._source_mask_filename = ImageFilename.parse(str(self.source_mask_path.relative_to(self.source_mask_dir)))
    return self._source_mask_filename
  
  @property
  def source_mask_filename_suffix_match(self):
    if not hasattr(self, "_source_mask_filename_suffix_match"):
      self._source_mask_filename_suffix_match = CELL_RESULT_FILE_SUFFIX_RE.match(self.source_mask_filename.suffix)
    return self._source_mask_filename_suffix_match

  @property
  def nucleus_index(self):
    return self.source_mask_filename_suffix_match["nucleus_index"]

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
  def summed_intensity(self):
    if not hasattr(self, "_summed_intensity"):
      self._summed_intensity = numpy.sum(self.rect_cropped_image, where=self.nuclear_mask, )
    return self._summed_intensity

  @property
  def area(self):
    if not hasattr(self, "_area"):
      self._area = numpy.count_nonzero(self.nuclear_mask)
    return self._area


def generate_cell_result_line_cli_str(masks, destination, source_images_dir, source_masks_dir):
  serialized_masks_params = (str(param) for image_or_mask_param in masks for param in image_or_mask_param)
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    "--source_images_dir=%s" % source_images_dir,
    "--source_masks_dir=%s" % source_masks_dir,
    *serialized_masks_params
  ])

@cli.log.LoggingApp
def generate_cell_result_line_cli(app):
  for mask_pair_start_index in (index * 2 for index in range(int(len(app.params.masks) / 2))):
    source_image, source_mask = app.params.masks[mask_pair_start_index:mask_pair_start_index + 2]
    try:
      GenerateCellResultLineJob(
        source_image,
        source_mask,
        app.params.destination,
        app.params.source_images_dir,
        app.params.source_masks_dir
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_cell_result_line_cli.add_param("masks", nargs="*")
generate_cell_result_line_cli.add_param("--destination", required=True)
generate_cell_result_line_cli.add_param("--source_images_dir", required=True)
generate_cell_result_line_cli.add_param("--source_masks_dir", required=True)

if __name__ == "__main__":
   generate_cell_result_line_cli.run()
