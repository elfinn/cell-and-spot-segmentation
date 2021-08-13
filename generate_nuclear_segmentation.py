import shlex
import logging
import re
import traceback
from copy import copy
from pathlib import Path

import cli.log
import matplotlib.pyplot as plt
import numpy
import scipy
import skimage.io
import skimage.segmentation
from cellpose import models, plot, transforms

from models.image_filename import ImageFilename
from models.paths import *


class GenerateNuclearSegmentationJob:
  def __init__(self, source, destination, source_dir, diameter):
    self.source_dir = Path(source_dir)
    self.source = source
    self.destination = destination
    self.diameter = diameter
    self.logger = logging.getLogger()

  def run(self):
    numpy.save(self.destination_filename, self.cellpose_filtered)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      global_destination_path = Path(self.destination)
      local_destination_path = Path(str(self.destination_image_filename)).parents[0]
      path_to_make = global_destination_path / local_destination_path
      self._destination_path = global_destination_path 
      if not path_to_make.exists():
        Path.mkdir(path_to_make, parents=True)
      elif not path_to_make.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def destination_filename(self):
    if not hasattr(self, "_destination_filename"):
      self._destination_filename = self.destination_path / str(self.destination_image_filename)
    return self._destination_filename

  @property
  def destination_image_filename(self):
    if not hasattr(self, "_destination_image_filename"):
      self._destination_image_filename = copy(self.source_image_filename)
      if hasattr(self.source_image_filename, "a"):
            self._destination_image_filename.a = None
      self._destination_image_filename.z = None
      self._destination_image_filename.c = None
      self._destination_image_filename.suffix = "_nuclear_segmentation"
      self._destination_image_filename.extension = "npy"
    return self._destination_image_filename

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

  @property
  def source_image_filename(self):
    if not hasattr(self, "_source_image_filename"):
      print("Source: %s" % self.source_path)
      print("Directory: %s" % self.source_dir)
      self._source_image_filename = ImageFilename.parse(str(self.source_path.relative_to(self.source_dir)))
    return self._source_image_filename

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = skimage.io.imread(self.source_path, as_gray=True)
    return self._image

  @property
  def cellpose_result(self):
    if not hasattr(self, "_cellpose_result"):
      model = models.Cellpose(model_type = "nuclei")
      self._cellpose_result = model.eval(self.image, diameter=self.diameter, channels=[[0,0]], resample=True)
    return self._cellpose_result

  @property
  def cellpose_filtered(self):
    if not hasattr(self, "_cellpose_filtered"):
      dilated = skimage.segmentation.expand_labels(self.cellpose_result[0], distance=3)
      self._cellpose_filtered = skimage.segmentation.clear_border(dilated)
    return self._cellpose_filtered


def generate_nuclear_segmentation_cli_str(sources, destination, source_dir, diameter):
  diameter_arguments = ["--diameter=%i" % diameter] if diameter != None else []
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    "--source_dir=%s" % source_dir,
    *diameter_arguments,
    *[str(source) for source in sources]
  ])

@cli.log.LoggingApp
def generate_nuclear_segmentation_cli(app):
  for source in app.params.sources:
    try:
      GenerateNuclearSegmentationJob(
        source,
        app.params.destination,
        app.params.source_dir,
        app.params.diameter
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_nuclear_segmentation_cli.add_param("sources", nargs="*")
generate_nuclear_segmentation_cli.add_param("--destination", required=True)
generate_nuclear_segmentation_cli.add_param("--source_dir", required=True)
generate_nuclear_segmentation_cli.add_param("--diameter", type=int, default=100)

if __name__ == "__main__":
   generate_nuclear_segmentation_cli.run()
