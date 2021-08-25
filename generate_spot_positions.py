import json
import logging
import shlex
import traceback
from copy import copy
from pathlib import Path
from functools import lru_cache

import cli.log
import numpy
import scipy.ndimage
import skimage.feature
import skimage.filters
import skimage.io
import skimage.segmentation

from models.generate_spot_positions_config import GenerateSpotPositionsConfig
from models.image_filename import ImageFilename
from models.paths import *


@lru_cache(maxsize=1)
def load_generate_spot_positions_configs(config_path):
  if config_path == None:
    return {}
  with open(config_path) as json_file:
    json_params_list = json.load(json_file)
    generate_spot_positions_configs = [
      GenerateSpotPositionsConfig.from_json_params(json_params)
      for json_params in json_params_list
    ]
    return {
      generate_spot_positions_config.channel:generate_spot_positions_config
      for generate_spot_positions_config in generate_spot_positions_configs
    }

class GenerateSpotPositionsJob:
  def __init__(
    self,
    source,
    destination,
    source_dir,
    user_determined_local_contrast_threshold=None,
    user_determined_radius=None,
    user_determined_global_threshold=None,
    config=None
  ):
    self.source = source
    self.destination = destination
    self.source_dir = Path(source_dir)
    self.user_determined_local_contrast_threshold = user_determined_local_contrast_threshold
    self.user_determined_radius = user_determined_radius
    self.user_determined_global_threshold = user_determined_global_threshold
    self.config = config
    self.logger = logging.getLogger()

  def run(self):
      for spot_index, spot in enumerate(self.spots):
        numpy.save(self.destination_filename_for_spot_index(spot_index), spot)

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
      self._source_image_filename = ImageFilename.parse(str(self.source_path.relative_to(self.source_dir)))
    return self._source_image_filename

  @property
  def threshold(self):
    if not hasattr(self, "_threshold"):
      self._threshold = self.image_background * self.local_contrast_threshold
    return self._threshold

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = numpy.load(self.source_path, allow_pickle=True)
    return self._image

  @property
  def filtered_image(self):
    if not hasattr(self, "_filtered_image"):
        self._filtered_image = skimage.filters.gaussian(self.image, sigma=self.peak_radius)
    return self._filtered_image

  @property
  def raw_spots(self):
    if not hasattr(self, "_raw_spots"):
      self._raw_spots = skimage.feature.blob_log(self.filtered_image, min_sigma=0.3, max_sigma=0.3, threshold=self.threshold)
    return self._raw_spots

  @property
  def global_filtered_spots(self):
    if not hasattr(self, "_global_filtered_spots"):
      self._global_filtered_spots = [
        (int(x), int(y))
        for x, y, _sigma
        in self.raw_spots 
        if self.image[int(x), int(y)] > self.global_contrast_threshold
      ]
    return self._global_filtered_spots

  @property
  def spots(self):
    if not hasattr(self, "_spots"):
      self._spots = [
        self.find_spot_center_of_mass(spot)
        for spot
        in self.global_filtered_spots
      ]
    return self._spots

  def find_spot_center_of_mass(self, integer_spot):
    local_box_x_min = max(0, integer_spot[0]-10)
    local_box_y_min = max(0, integer_spot[1]-10)
    local_box_x_max = min(integer_spot[0]+10, numpy.shape(self.image)[0])
    local_box_y_max = min(integer_spot[1]+10, numpy.shape(self.image)[1])
    
    local_background = numpy.percentile(self.image[local_box_x_min:local_box_x_max, local_box_y_min:local_box_y_max], 25)

    marker = skimage.segmentation.flood(
      self.image,
      integer_spot,
      tolerance=(self.image[integer_spot] - local_background) / 2
    )
    return scipy.ndimage.center_of_mass(self.image, marker)
  
  @property
  def image_background(self):
    if not hasattr(self, "_image_background"):
      self._image_background = numpy.percentile(self.image, 75)
    return self._image_background

  @property
  def local_contrast_threshold(self):
    if self.user_determined_local_contrast_threshold != None:
      return self.user_determined_local_contrast_threshold
    if self.channel_specific_config != None:
      return self.channel_specific_config.local_contrast_threshold
    if self.source_image_filename.c == 3:
      return 4
    return 2.75

  @property
  def peak_radius(self):
    if self.user_determined_radius != None:
      return self.user_determined_radius
    if self.channel_specific_config != None:
      return self.channel_specific_config.peak_radius
    if self.source_image_filename.c == 3:
      return 3
    return 1

  @property
  def global_contrast_threshold(self):
    if self.user_determined_global_threshold != None:
      return self.user_determined_global_threshold
    if self.channel_specific_config != None:
      return self.channel_specific_config.global_contrast_threshold
    return 0

  @property
  def channel_specific_config(self):
    if self.config != None:
      configs = load_generate_spot_positions_configs(self.config)
      if self.source_image_filename.c in configs:
        return configs[self.source_image_filename.c]

def generate_spot_positions_cli_str(sources, destination, source_dir, config=None):
  config_arguments = ["--config=%s" % config] if config != None else []
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    "--source_dir=%s" % source_dir,
    *config_arguments,
    *[str(source) for source in sources]
  ])

@cli.log.LoggingApp
def generate_spot_positions_cli(app):
  for source in app.params.sources:
    try:
      GenerateSpotPositionsJob(
        source,
        app.params.destination,
        app.params.source_dir,
        config=app.params.config
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_spot_positions_cli.add_param("sources", nargs="*")
generate_spot_positions_cli.add_param("--destination", required=True)
generate_spot_positions_cli.add_param("--source_dir", required=True)
generate_spot_positions_cli.add_param("--config")

if __name__ == "__main__":
   generate_spot_positions_cli.run()
