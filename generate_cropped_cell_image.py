import cli.log
import traceback
import numpy
import skimage.measure
import re
import skimage.io
import skimage.util

import matplotlib.pyplot as plt

from models.paths import *
from models.nuclear_mask import NuclearMask

class GenerateCroppedCellImageJob:
  def __init__(self, source_image, source_mask, destination):
    self.source_image = source_image
    self.source_mask = source_mask
    self.destination = destination

  def run(self):
    pass
    #numpy.save(self.destination_filename, self.masked_cropped_image)

  @property
  def destination_filename(self):
    return self.destination_path / self.source_mask_path.stem.replace("C01_nuclear_mask_", self.channel_replace_string)

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def source_image_path(self):
    if not hasattr(self, "_source_image_path"):
      self._source_image_path = source_path(self.source_image)
    return self._source_image_path

  @property
  def source_mask_path(self):
    if not hasattr(self, "_source_mask_path"):
      self._source_mask_path = source_path(self.source_mask)
    return self._source_mask_path

  @property
  def source_channel(self):
    if not hasattr(self, "_source_channel"):
        channel_pattern = re.compile(r'(C\d{2})_maximum_projection.png')
        match = channel_pattern.search(self.source_image)
        if not match:
            raise Exception("Source image does not specify channel")
        else: 
            self._source_channel = match.group(1)
    return self._source_channel

  @property
  def channel_replace_string(self):
    if not hasattr(self, "_channel_replace_string"):
        self._channel_replace_string = self.source_channel + "_cropped_"
    return self._channel_replace_string

  @property
  def nuclear_mask(self):
    if not hasattr(self, "_nuclear_mask"):
      self._nuclear_mask = numpy.load(self.source_mask_path, allow_pickle=True).item().mask
    return self._nuclear_mask

  @property
  def nuclear_offset(self):
    if not hasattr(self, "_nuclear_offset"):
      self._nuclear_offset = numpy.load(self.source_mask_path, allow_pickle=True).item().offset
    return self._nuclear_offset

  @property
  def image(self):
      if not hasattr(self, "_image"):
          self._image = skimage.io.imread(self.source_image_path, as_gray=True)
      return self._image

  @property
  def rect_cropped_image(self):
    if not hasattr(self, "_rect_cropped_image"):
        [min_row, min_col] = self.nuclear_offset
        shape = numpy.shape(self.nuclear_mask)
        self._rect_cropped_image = self.image[min_row:min_row+shape[0], min_col:min_col+shape[1]]
    return self._rect_cropped_image

  @property
  def min_in_nucleus(self):
    if not hasattr(self, "_min_in_nucleus"):
      self._min_in_nucleus = numpy.amin(self.rect_cropped_image, where=self.nuclear_mask, initial=100000)
    return self._min_in_nucleus

  @property
  def max_in_nucleus(self):
    if not hasattr(self, "_max_in_nucleus"):
      self._max_in_nucleus = numpy.amax(self.rect_cropped_image, where=self.nuclear_mask, initial=0)
    return self._max_in_nucleus

  @property
  def masked_cropped_image(self):
    if not hasattr(self, "_masked_cropped_image"):
      normed_image = skimage.exposure.rescale_intensity(self.rect_cropped_image, in_range=(self.min_in_nucleus, self.max_in_nucleus), out_range=(0,1))
      inverted_image = skimage.util.invert(normed_image)
      self._masked_cropped_image = inverted_image*self.nuclear_mask
    return self._masked_cropped_image
          
def generate_cropped_cell_image_cli_str(source_image, source_mask, destination):
  return "pipenv run python %s '%s' '%s' '%s'" % (__file__, source_image, source_mask, destination)

@cli.log.LoggingApp
def generate_cropped_cell_image_cli(app):
  try:
    GenerateCroppedCellImageJob(
      app.params.source_image,
      app.params.source_mask,
      app.params.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_cropped_cell_image_cli.add_param("source_image")
generate_cropped_cell_image_cli.add_param("source_mask")
generate_cropped_cell_image_cli.add_param("destination")

if __name__ == "__main__":
   generate_cropped_cell_image_cli.run()
