import logging
import shlex
import traceback
from copy import copy
from pathlib import Path

import cli.log
import numpy
import scipy.ndimage
import skimage.feature
import skimage.filters
import skimage.io
import skimage.segmentation

from models.image_filename import ImageFilename
from models.paths import *


class GenerateSpotPositionsJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination
    self.logger = logging.getLogger()

  def run(self):
      for spot_index, spot in enumerate(self.spots):
        numpy.save(self.destination_filename_for_spot_index(spot_index), spot)

  @property
  def destination_path(self):
   if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
   return self._destination_path

  def destination_filename_for_spot_index(self, spot_index):
    destination_image_filename = copy(self.source_image_filename)
    nucleus_index = self.source_image_filename.suffix.split("_")[-1]
    destination_image_filename.suffix = "_nucleus_%s_spot_%i" % (nucleus_index, spot_index)
    return self.destination_path / str(destination_image_filename)

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

  @property
  def source_image_filename(self):
    if not hasattr(self, "_source_image_filename"):
      self._source_image_filename = ImageFilename.parse(self.source_path.name)
    return self._source_image_filename

  @property
  def threshold(self):
    if not hasattr(self, "_threshold"):
      self._threshold = self.image_background * self.contrast_threshold
    return self._threshold

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = numpy.load(self.source_path, allow_pickle=True)
    return self._image

  @property
  def filtered_image(self):
    if not hasattr(self, "_filtered_image"):
        self._filtered_image = skimage.filters.gaussian(self.image, sigma=2)
    return self._filtered_image

  @property
  def spots(self):
    if not hasattr(self, "_spots"):
      self._spots = [
        self.find_spot_center_of_mass((int(x), int(y)))
        for x, y, _sigma
        in skimage.feature.blob_log(self.filtered_image, min_sigma=0.3, max_sigma=0.3, threshold=self.threshold)
      ]
    return self._spots

  def find_spot_center_of_mass(self, integer_spot):
    marker = skimage.segmentation.flood(
      self.image,
      integer_spot,
      tolerance=(self.image[integer_spot] - self.image_background) / 2
    )
    return scipy.ndimage.center_of_mass(self.image, marker)
  
  @property
  def image_background(self):
    if not hasattr(self, "_image_background"):
      self._image_background = numpy.percentile(self.image, 75)
    return self._image_background

  @property
  def contrast_threshold(self):
    if self.source_image_filename.c == 3:
      return 4
    return 2.75

def generate_spot_positions_cli_str(sources, destination):
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    *[str(source) for source in sources]
  ])

@cli.log.LoggingApp
def generate_spot_positions_cli(app):
  for source in app.params.sources:
    try:
      GenerateSpotPositionsJob(
        source,
        app.params.destination,
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_spot_positions_cli.add_param("sources", nargs="*")
generate_spot_positions_cli.add_param("--destination", required=True)

if __name__ == "__main__":
   generate_spot_positions_cli.run()
