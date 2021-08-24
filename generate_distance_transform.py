import copy
import logging
import shlex
import traceback

import cli.log
import numpy
from scipy import ndimage

from models.paths import *


class GenerateDistanceTransformJob:
  def __init__(self, source, destination, source_dir):
    self.source = source
    self.destination = destination
    self.source_dir = Path(source_dir)

  def run(self):
    numpy.save(self.destination_filename, self.distance_transform)

  @property
  def destination_filename(self):
    source_relative_path = str(self.source_path.relative_to(self.source_dir))
    return self.destination_path / source_relative_path.replace("_nuclear_mask_", "_distance_transform_")

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
      global_destination_path = Path(self.destination)
      local_destination_path = Path(str(self.source_path.relative_to(self.source_dir))).parents[0]
      path_to_make = global_destination_path / local_destination_path
      self._destination_path = global_destination_path 
      if not path_to_make.exists():
        Path.mkdir(path_to_make, parents=True)
      elif not path_to_make.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

def generate_distance_transform_cli_str(sources, destination, source_dir):
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    "--source_dir=%s" % source_dir,
    *[str(source) for source in sources]
  ])

@cli.log.LoggingApp
def generate_distance_transform_cli(app):
  for source in app.params.sources:
    try:
      GenerateDistanceTransformJob(
        source,
        app.params.destination,
        app.params.source_dir,
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_distance_transform_cli.add_param("sources", nargs="*")
generate_distance_transform_cli.add_param("--destination", required=True)
generate_distance_transform_cli.add_param("--source_dir", required=True)

if __name__ == "__main__":
   generate_distance_transform_cli.run()
