import shlex
import csv
import logging
import re
import traceback
from copy import copy
from pathlib import Path

import cli.log
import numpy

from models.image_filename import ImageFilename
from models.paths import *

SPOT_RESULT_FILE_SUFFIX_RE = re.compile("_nucleus_(?P<nucleus_index>\d{3})_spot_(?P<spot_index>\d+)")

class GenerateSpotResultLineJob:
  def __init__(self, spot_source, z_centers_source_directory, distance_transforms_source_directory, destination):
    self.spot_source = spot_source
    self.z_centers_source_directory = z_centers_source_directory
    self.distance_transforms_source_directory = distance_transforms_source_directory
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
      "experiment": self.source_image_filename.experiment,
      "well": self.source_image_filename.well,
      "timepoint": self.source_image_filename.t,
      "field": self.source_image_filename.f,
      "timeline": self.source_image_filename.l,
      "channel": self.source_image_filename.c,
      "nucleus_index": self.nucleus_index,
      "spot_index": self.spot_index,
      "center_x": self.center_x,
      "center_y": self.center_y,
      "center_z": self.center_z,
      "center_r": self.center_r,
    }

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def destination_filename(self):
    return self.destination_path / ("%s.csv" % self.source_path.stem)

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.spot_source)
    return self._source_path
  
  @property
  def source_image_filename(self):
    if not hasattr(self, "_source_image_filename"):
      self._source_image_filename = ImageFilename.parse(self.source_path.name)
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
      self._spot = numpy.load(self.source_path)
    return self._spot

  @property
  def center_x(self):
    return self.spot[1]

  @property
  def center_y(self):
    return self.spot[0]

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
      self._z_center_image_filename.suffix = "_z_center_nuclear_mask_%s" % self.nucleus_index
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
  def distance_transform_image_filename(self):
    if not hasattr(self, "_distance_transform_image_filename"):
      self._distance_transform_image_filename = copy(self.source_image_filename)
      self._distance_transform_image_filename.suffix = "_distance_transform_%s" % self.nucleus_index
      self._distance_transform_image_filename.a = None
      self._distance_transform_image_filename.z = None
      self._distance_transform_image_filename.c = None
    return self._distance_transform_image_filename
  
  @property
  def distance_transform_image_path(self):
    if not hasattr(self, "_distance_transform_image_path"):
      self._distance_transform_image_path = self.distance_transforms_source_directory_path / str(self.distance_transform_image_filename)
    return self._distance_transform_image_path

  @property
  def distance_transform_image(self):
    if not hasattr(self, "_distance_transform_image"):
      self._distance_transform_image = numpy.load(self.distance_transform_image_path)
    return self._distance_transform_image
  
  @property
  def center_r(self):
    return self.distance_transform_image[self.pixel_center]

def generate_spot_result_line_cli_str(spot_sources, z_centers_source_directory, distance_transforms_source_directory, destination):
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--z_centers_source_directory=%s" % z_centers_source_directory,
    "--distance_transforms_source_directory=%s" % distance_transforms_source_directory,
    "--destination=%s" % destination,
    *[str(spot_source) for spot_source in spot_sources]
  ])

@cli.log.LoggingApp
def generate_spot_result_line_cli(app):
  for spot_source in app.params.spot_sources:
    try:
      GenerateSpotResultLineJob(
        spot_source,
        app.params.z_centers_source_directory,
        app.params.distance_transforms_source_directory,
        app.params.destination,
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_spot_result_line_cli.add_param("spot_sources", nargs="*")
generate_spot_result_line_cli.add_param("--z_centers_source_directory", required=True)
generate_spot_result_line_cli.add_param("--distance_transforms_source_directory", required=True)
generate_spot_result_line_cli.add_param("--destination", required=True)

if __name__ == "__main__":
   generate_spot_result_line_cli.run()
