import cli.log
import traceback
import numpy
import logging
from scipy import ndimage

from models.paths import *

class GenerateDistanceTransformJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination

  def run(self):
    numpy.save(self.destination_filename, self.distance_transform)

  @property
  def destination_filename(self):
    return self.destination_path / self.source_path.stem.replace("_nuclear_mask_", "_distance_transform_")

  @property
  def distance_transform(self):
    if not hasattr(self, "_distance_transform"):
       raw_transform = ndimage.distance_transform_edt(self.nuclear_mask)
       normed_transform = raw_transform/numpy.amax(raw_transform)
       self._distance_transform = 1 - normed_transform
    return self._distance_transform
  
  @property
  def nuclear_mask(self):
    if not hasattr(self, "_nuclear_mask"):
      self._nuclear_mask = numpy.load(self.source_path, allow_pickle=True).item().mask
    return self._nuclear_mask

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

@cli.log.LoggingApp
def generate_distance_transform(app):
  try:
    GenerateDistanceTransformJob(
      app.params.source,
      app.params.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_distance_transform.add_param("source", default="C:\\\\Users\\finne\\Documents\\python\\MaxProjections\\AssayPlate_PerkinElmer_CellCarrier-384_B07_T0001F009L01A01ZXXC01_maximum_projection.png", nargs="?")
generate_distance_transform.add_param("destination", default="C:\\\\Users\\finne\\Documents\\python\\NucMasks", nargs="?")

if __name__ == "__main__":
   generate_distance_transform.run()
