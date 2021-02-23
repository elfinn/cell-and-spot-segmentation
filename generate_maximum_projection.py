import shlex
import logging
import re
import traceback
from pathlib import Path

import cli.log
import matplotlib.pyplot as plt
import numpy

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
    numpy.save(str(self.destination_path / self.z_center_destination_filename), self.z_center)

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
  def z_center(self):
    if not hasattr(self, "_z_center"):
      self.process_source_z_sliced_images()
    return self._z_center

  def process_source_z_sliced_images(self):
    if hasattr(self, "_z_center") or hasattr(self, "_maximum_projection"):
      raise Exception("already computed")

    shaped = False
    maximum_projection = None
    summed_z_values = None
    weighted_summed_z_values = None
    for source_z_sliced_image in self.source_z_sliced_images:
      if not shaped:
        shaped = True
        shape = numpy.shape(source_z_sliced_image.image)
        maximum_projection = numpy.empty(shape)
        summed_z_values = numpy.empty(shape)
        weighted_summed_z_values = numpy.empty(shape)

      maximum_projection = numpy.fmax(maximum_projection, source_z_sliced_image.image)
      summed_z_values = summed_z_values + source_z_sliced_image.image
      weighted_summed_z_values = weighted_summed_z_values + (source_z_sliced_image.image * source_z_sliced_image.z)

    summed_z_values = numpy.fmax(summed_z_values, numpy.ones_like(summed_z_values))
    self._maximum_projection = maximum_projection
    self._z_center = (weighted_summed_z_values/summed_z_values).astype(numpy.float16)

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
  def z_center_destination_filename(self):
    return "%s%s" % (self.destination_filename_prefix, "_z_center")

def generate_maximum_projection_cli_str(source_directory, filename_patterns, destination):
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    "--source_directory=%s" % source_directory,
    *(str(filename_pattern) for filename_pattern in filename_patterns)
  ])

@cli.log.LoggingApp
def generate_maximum_projection_cli(app):
  for filename_pattern in app.params.filename_patterns:
    try:
      GenerateMaximumProjectionJob(
        app.params.source_directory,
        filename_pattern,
        app.params.destination
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_maximum_projection_cli.add_param("--source_directory", required=True)
generate_maximum_projection_cli.add_param("--destination", required=True)
generate_maximum_projection_cli.add_param("filename_patterns", nargs="*")

if __name__ == "__main__":
   generate_maximum_projection_cli.run()
