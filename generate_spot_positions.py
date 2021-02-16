import cli.log
import logging
from pathlib import Path
import traceback
from models.paths import *
from models.image_filename import ImageFilename
import skimage.filters
import skimage.io
import skimage.feature
import numpy

class GenerateSpotPositionsJob:
  def __init__(self, source, destination, contrast_threshold):
    self.source = source
    self.destination = destination
    self.contrast_threshold = contrast_threshold
    self.logger = logging.getLogger()

  def run(self):
      pass

  @property
  def destination_path(self):
   if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
   return self._destination_path

  @property
  def destination_filename(self):
    if not hasattr(self, "_destination_filename"):
      self._destination_filename = self.destination_path / self.source_path.stem.replace("_cropped_", "_positions_")
    return self._destination_filename

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

  @property
  def threshold(self):
    if not hasattr(self, "_threshold"):
      self._threshold = numpy.percentile(self.image, 75)*self.contrast_threshold
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
      self._spots = skimage.feature.blob_log(self.filtered_image, min_sigma=0.3, max_sigma=0.3, threshold=self.threshold)
    return self._spots



def generate_spot_positions_cli_str(source, destination):
  result = "pipenv run python %s '%s' '%s'" % (__file__, source, destination)
  return result

@cli.log.LoggingApp
def generate_spot_positions_cli(app):
  try:
    GenerateSpotPositionsJob(
      app.params.source,
      app.params.destination,
      app.params.contrast_threshold
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_spot_positions_cli.add_param("source", default="C:\\\\Users\\finne\\Documents\\python\\cropped_cells\\384_B07_T0001F007L01A01ZXXC03_cropped_016.npy", nargs="?")
generate_spot_positions_cli.add_param("destination", default="C:\\\\Users\\finne\\Documents\\python\\spot_positions\\", nargs="?")
generate_spot_positions_cli.add_param("--contrast_threshold", default=3, type=int)

if __name__ == "__main__":
   generate_spot_positions_cli.run()