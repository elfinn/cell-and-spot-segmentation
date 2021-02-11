import cli.log
import logging
from pathlib import Path
import traceback
import numpy
import matplotlib.pyplot as plt
import re

from models.paths import *
from models.z_sliced_image import ZSlicedImage

class GenerateMaximumProjectionJob:
  def __init__(self, source_directory, filename_pattern, destination):
    self.source_directory = source_directory
    self.filename_pattern = filename_pattern
    self.destination = destination
    self.logger = logging.getLogger()

  def run(self):
    plt.imsave(str(self.destination_path / self.maximum_projection_destination_filename), self.maximum_projection, cmap="Greys")
    numpy.save(self.destination_path / self.weighted_center_destination_filename, self.weighted_center)

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
    return self.source_directory_path.glob(self.filename_pattern)

  @property
  def maximum_projection(self):
    if not hasattr(self, "_maximum_projection"):
      self.process_source_z_sliced_images()
    return self._maximum_projection

  @property
  def weighted_center(self):
    if not hasattr(self, "_weighted_center"):
      self.process_source_z_sliced_images()
    return self._weighted_center

  def process_source_z_sliced_images(self):
    if hasattr(self, "_weighted_center") or hasattr(self, "_maximum_projection"):
      raise Exception("already computed")

    shaped = False
    maximum_projection = None
    summed_values = None
    weighted_summed_values = None
    for source_z_sliced_image in self.source_z_sliced_images:
      if not shaped:
        shaped = True
        shape = numpy.shape(source_z_sliced_image.numpy_array)
        maximum_projection = numpy.empty(shape)
        summed_values = numpy.empty(shape)
        weighted_summed_values = numpy.empty(shape)
      
      maximum_projection = numpy.fmax(maximum_projection, source_z_sliced_image.numpy_array)
      summed_values = summed_values + source_z_sliced_image.numpy_array
      weighted_summed_values = weighted_summed_values + (source_z_sliced_image.numpy_array * source_z_sliced_image.z)

    summed_values = numpy.fmax(summed_values, numpy.ones_like(summed_values))
    self._maximum_projection = maximum_projection
    self._weighted_center = (weighted_summed_values/summed_values).astype(numpy.float16)

  @property
  def source_z_sliced_images(self):
    return (ZSlicedImage(source_file_path) for source_file_path in self.source_file_paths)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = Path(self.destination)
      if not self._destination_path.exists():
        Path.mkdir(self._destination_path, parents=True)
      elif not self._destination_path.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def destination_filename_prefix(self):
    return Path(self.filename_pattern.replace("?", "X")).stem
  
  @property
  def maximum_projection_destination_filename(self):
    return "%s%s" % (self.destination_filename_prefix, "_maximum_projection.png")

  @property
  def weighted_center_destination_filename(self):
    return "%s%s" % (self.destination_filename_prefix, "_weighted_center.npy")

def generate_maximum_projection_cli_str(source_directory, filename_pattern, destination):
  return "pipenv run python %s '%s' '%s' '%s'" % (__file__, source_directory, filename_pattern, destination)

@cli.log.LoggingApp
def generate_maximum_projection_cli(app):
  try:
    GenerateMaximumProjectionJob(
      app.params.source_directory,
      app.params.filename_pattern,
      app.params.destination
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_maximum_projection_cli.add_param("source_directory")
generate_maximum_projection_cli.add_param("filename_pattern")
generate_maximum_projection_cli.add_param("destination")

if __name__ == "__main__":
   generate_maximum_projection_cli.run()
