import shlex
import csv
import logging
import re
import traceback
from copy import copy
from pathlib import Path

import argparse
import numpy

from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob
from models.paths import *

SPOT_RESULT_FILE_SUFFIX_RE = re.compile("_nucleus_(?P<nucleus_index>\d{3})_spot_(?P<spot_index>\d+)")

class GenerateSpotResultLineJob:
  def __init__(
    self,
    spot_source,
    spot_source_directory,
    z_centers_source_directory,
    distance_transforms_source_directory,
    nuclear_masks_source_directory,
    destination
  ):
    self.spot_source = spot_source
    self.spot_source_directory = Path(spot_source_directory)
    self.z_centers_source_directory = z_centers_source_directory
    self.distance_transforms_source_directory = distance_transforms_source_directory
    self.nuclear_masks_source_directory = nuclear_masks_source_directory
    self.destination = destination
  
  def run(self):
    with open(self.destination_filename, 'w') as csv_file:
      csv_writer = csv.DictWriter(csv_file, self.csv_values.keys())
      csv_writer.writeheader()
      csv_writer.writerow(self.csv_values)

  @property
  def csv_values(self):
    return {
      "filename": str(self.source_image_filename),
      "date": self.date,
      "group" : self.source_image_filename.group,
      "position": self.source_image_filename.position,
      "field": self.source_image_filename.f,
      "channel": self.source_image_filename.c,
      "nucleus_index": self.nucleus_index,
      "spot_index": self.spot_index,
      "center_x": self.center_x,
      "center_y": self.center_y,
      "center_z": self.center_z,
      "center_r": self.center_r,
      "area": self.area,
      "eccentricity": self.eccentricity,
      "solidity": self.solidity,
      "nuclear_mask_offset_x": self.nuclear_mask_offset_x,
      "nuclear_mask_offset_y": self.nuclear_mask_offset_y
    }

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      global_destination_path = Path(self.destination)
      local_destination_path = Path(str(self.source_path.relative_to(self.spot_source_directory))).parents[0]
      path_to_make = global_destination_path / local_destination_path
      self._destination_path = global_destination_path 
      if not path_to_make.exists():
        Path.mkdir(path_to_make, parents=True)
      elif not path_to_make.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def destination_filename(self):
    if not hasattr (self, "_destination_filename"):
        destination_line_filename = copy(self.source_image_filename)
        destination_line_filename.extension = "csv"
        self._destination_filename = self.destination_path / str(destination_line_filename)
    return self._destination_filename

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.spot_source)
    return self._source_path
  
  @property
  def source_image_filename(self):
    if not hasattr(self, "_source_image_filename"):
      self._source_image_filename = ImageFilename.parse(str(self.source_path.relative_to(self.spot_source_directory)))
    return self._source_image_filename
  
  @property
  def source_image_filename_suffix_match(self):
    if not hasattr(self, "_source_image_filename_suffix_match"):
      self._source_image_filename_suffix_match = SPOT_RESULT_FILE_SUFFIX_RE.match(self.source_image_filename.suffix)
    return self._source_image_filename_suffix_match

  @property
  def nucleus_index(self):
    return self.source_image_filename_suffix_match["nucleus_index"]

  @property
  def spot_index(self):
    return self.source_image_filename_suffix_match["spot_index"]
  
  @property
  def spot(self):
    if not hasattr(self, "_spot"):
      self._spot = numpy.load(self.source_path, allow_pickle=True)
    return self._spot

  @property
  def date(self):
    long_date_re = re.compile("(\d{4})-(\d{2})-(\d{2})")
    if not hasattr(self, "_date"):
      self._date = self.source_image_filename.date
      long_date_match = long_date_re.match(self._date)
      if(long_date_match):
        self._date = str(long_date_match[1])+str(long_date_match[2])+str(long_date_match[3])
    return self._date
        

  @property
  def center_x(self):
    return self.spot[4]

  @property
  def center_y(self):
    return self.spot[3]

  @property
  def area(self):
    return self.spot[0]

  @property
  def eccentricity(self):
    return self.spot[1]

  @property
  def solidity(self):
    return self.spot[2]

  @property
  def z_centers_source_directory_path(self):
    if not hasattr(self, "_z_centers_source_directory_path"):
      self._z_centers_source_directory_path = source_path(self.z_centers_source_directory)
      if not self._z_centers_source_directory_path.is_dir():
        raise Exception("z centers source directory does not exist")
    return self._z_centers_source_directory_path

  @property
  def distance_transforms_source_directory_path(self):
    if not hasattr(self, "_distance_transforms_source_directory_path"):
      self._distance_transforms_source_directory_path = source_path(self.distance_transforms_source_directory)
      if not self._distance_transforms_source_directory_path.is_dir():
        raise Exception("distance transforms source directory does not exist")
    return self._distance_transforms_source_directory_path

  @property
  def z_center_image_filename(self):
    if not hasattr(self, "_z_center_image_filename"):
      self._z_center_image_filename = copy(self.source_image_filename)
      self._z_center_image_filename.suffix = "_z_center_nucleus_%s" % self.nucleus_index
    return self._z_center_image_filename

  @property
  def z_center_image_path(self):
    if not hasattr(self, "_z_center_image_path"):
      self._z_center_image_path = self.z_centers_source_directory_path / str(self.z_center_image_filename)
    return self._z_center_image_path

  @property
  def z_center_image(self):
    if not hasattr(self, "_z_center_image"):
      self._z_center_image = numpy.load(self.z_center_image_path)
    return self._z_center_image
  
  @property
  def pixel_center(self):
    return (round(self.center_y), round(self.center_x))

  @property
  def center_z(self):
    return self.z_center_image[self.pixel_center]

  @property
  def distance_transform_image_path(self):
    if not hasattr(self, "_distance_transform_image_filename"):
      distance_transform_filename_glob = ImageFilenameGlob.from_image_filename(self.source_image_filename, excluding_keys = ["a", "c", "z"])
      distance_transform_filename_glob.glob.suffix = "_dt_%s" % self.nucleus_index
    return next(self.distance_transforms_source_directory_path.rglob(str(distance_transform_filename_glob)))
  
  @property
  def distance_transform_image(self):
    if not hasattr(self, "_distance_transform_image"):
      self._distance_transform_image = numpy.load(self.distance_transform_image_path)
    return self._distance_transform_image
  
  @property
  def center_r(self):
    return self.distance_transform_image[self.pixel_center]
  
  @property
  def nuclear_mask_offset_x(self):
    return self.nuclear_mask.offset[0]

  @property
  def nuclear_mask_offset_y(self):
    return self.nuclear_mask.offset[1]

  @property
  def nuclear_mask(self):
    if not hasattr(self, "_nuclear_mask"):
      self._nuclear_mask = numpy.load(self.nuclear_mask_path, allow_pickle=True).item()
    return self._nuclear_mask
  
  @property
  def nuclear_masks_source_directory_path(self):
    if not hasattr(self, "_nuclear_masks_source_directory_path"):
      self._nuclear_masks_source_directory_path = source_path(self.nuclear_masks_source_directory)
      if not self._nuclear_masks_source_directory_path.is_dir():
        raise Exception("z centers source directory does not exist")
    return self._nuclear_masks_source_directory_path

  @property
  def nuclear_mask_path(self):
    if not hasattr(self, "_nuclear_mask_path"):
      nuclear_mask_glob = ImageFilenameGlob.from_image_filename(self.source_image_filename, excluding_keys = ["a", "c", "z"])
      nuclear_mask_glob.glob.suffix = "_nucleus_%s" % self.nucleus_index
    return next(self.nuclear_masks_source_directory_path.rglob(str(nuclear_mask_glob)))

def generate_spot_result_line_cli_str(
  z_centers_source_directory,
  distance_transforms_source_directory,
  nuclear_masks_source_directory,
  spot_source_directory,
  destination
):
  return shlex.join([
    "python3",
    __file__,
    "--z_centers_source_directory=%s" % z_centers_source_directory,
    "--distance_transforms_source_directory=%s" % distance_transforms_source_directory,
    "--nuclear_masks_source_directory=%s" % nuclear_masks_source_directory,
    "--spot_source_directory=%s" % spot_source_directory,
    "--destination=%s" % destination
  ])

parser = argparse.ArgumentParser()
parser.add_argument("spot_sources", nargs="*")
parser.add_argument("--z_centers_source_directory", required=True)
parser.add_argument("--distance_transforms_source_directory", required=True)
parser.add_argument("--nuclear_masks_source_directory", required=True)
parser.add_argument("--spot_source_directory", required=True)
parser.add_argument("--destination", required=True)

def generate_spot_result_line_cli(parser):
  args = parser.parse_args()
  for spot_source in args.spot_sources:
    try:
      GenerateSpotResultLineJob(
        spot_source,
        args.z_centers_source_directory,
        args.distance_transforms_source_directory,
        args.nuclear_masks_source_directory,
        args.spot_source_directory,
        args.destination,
      ).run()
    except Exception as exception:
      traceback.print_exc()

if __name__ == "__main__":
   generate_spot_result_line_cli(parser)
