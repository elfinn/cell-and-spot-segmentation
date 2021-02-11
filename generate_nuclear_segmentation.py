import cli.log
import logging
from pathlib import Path
import traceback
import numpy
import scipy
import skimage.io
import skimage.segmentation
import matplotlib.pyplot as plt
import re
from models.paths import *
from models.image_filename import ImageFilename
from cellpose import models, plot, transforms

class GenerateNuclearSegmentationJob:
  def __init__(self, source, destination, diameter):
    self.source = source
    self.destination = destination
    self.diameter = diameter
    self.logger = logging.getLogger()

  def run(self):
    numpy.save(self.destination_filename, self.cellpose_filtered)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def destination_filename(self):
    if not hasattr(self, "_destination_filename"):
      self._destination_filename = self.destination_path / self.source_path.stem.replace("_maximum_projection", "_nuclear_segmentation")
    return self._destination_filename

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = skimage.io.imread(self.source_path)
    return self._image

  @property
  def cellpose_result(self):
    if not hasattr(self, "_cellpose_result"):
      model = models.Cellpose(model_type = "nuclei")
      self._cellpose_result = model.eval(self.image, diameter=self.diameter, channels=[[0,0]], invert=True)
    return self._cellpose_result

  @property
  def cellpose_filtered(self):
    if not hasattr(self, "_cellpose_filtered"):
      dilated = skimage.segmentation.expand_labels(self.cellpose_result[0], distance=1)
      self._cellpose_filtered = skimage.segmentation.clear_border(dilated)
    return self._cellpose_filtered
  

def generate_nuclear_segmentation_cli_str(source, destination, diameter):
  result = "pipenv run python %s '%s' '%s'" % (__file__, source, destination)
  if diameter:
    result = "%s --diameter %i" % (result, diameter)
  return result

@cli.log.LoggingApp
def generate_nuclear_segmentation_cli(app):
  try:
    GenerateNuclearSegmentationJob(
      app.params.source,
      app.params.destination,
      app.params.diameter
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_nuclear_segmentation_cli.add_param("source", default="C:\\\\Users\\finne\\Documents\\python\\MaxProjections\\AssayPlate_PerkinElmer_CellCarrier-384_B07_T0001F009L01A01ZXXC01_maximum_projection.png", nargs="?")
generate_nuclear_segmentation_cli.add_param("destination", default="C:\\\\Users\\finne\\Documents\\python\\NucMasks", nargs="?")
generate_nuclear_segmentation_cli.add_param("--diameter", type=int, default=100)

if __name__ == "__main__":
   generate_nuclear_segmentation_cli.run()
