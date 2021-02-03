import cli.log
import logging
from pathlib import Path
import traceback
import numpy
import scipy
from PIL import Image
import matplotlib.pyplot as plt
import re

class GenerateMaximumProjectionJob:
  def __init__(self, source_directory, source_file_pattern, destination):
    self.source_directory = source_directory
    self.source_file_pattern = source_file_pattern
    self.destination = destination
    self.logger = logging.getLogger()

  def run(self):
    # find all the images
    for f in self.source_file_paths:
      img = ZSlicedImage(f)
      #printMyImage = plt.imshow(img.numpy_array)
      #plt.show()
      self.logger.warning("Z-slice %s", img.z)
      
    # maximially project them
    MIPToPrint = plt.imshow(self.MaxProj)
    plt.show()

    # compute the z-axis distance distribution
    WeightedCenterToPrint = plt.imshow(self.WeightedCenter)
    plt.show()
    
    # serialize it all out, probably via `numpy.save(Path(self.destination) / ("%_maximal_projection.npy" % self.source_image_prefix))`
    
    
    pass

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
  def source_directory_path(self):
    if not hasattr(self, "_source_directory_path"):
      self._source_directory_path = Path(self.source_directory)
      if not self._source_directory_path.is_dir():
        raise Exception("image directory does not exist")
    return self._source_directory_path

  @property
  def source_file_paths(self):
    return self.source_directory_path.glob(self.source_file_pattern)

  @property
  def MaxProj(self):
    if not hasattr(self, "_MaxProj"):
      self._MaxProj = numpy.empty((1998, 1998))
      for f in self.source_file_paths:
        img = ZSlicedImage(f)
        self._MaxProj = numpy.fmax(self._MaxProj, img.numpy_array)
    return self._MaxProj

  @property
  def WeightedCenter(self):
    if not hasattr(self, "_WeightedCenter"):
      summedValues = numpy.empty((1998, 1998))
      weightedSummedValues = numpy.empty((1998,1998))
      for f in self.source_file_paths:
        img = ZSlicedImage(f)
        summedValues = summedValues + img.numpy_array
        weightedSummedValues = weightedSummedValues + img.z*img.numpy_array
      self._WeightedCenter = weightedSummedValues/summedValues
      return self._WeightedCenter


class ZSlicedImage:
  def __init__(self, path):
    self.path = path

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = Image.open(self.path)
    return self._image

  @property
  def numpy_array(self):
    if not hasattr(self, "_numpy_array"):
      self._numpy_array = numpy.asarray(self.image)
    return self._numpy_array

  @property
  def z(self):
    if not hasattr(self, "_z"):
      pattern = re.compile('Z(\\d\\d)C\\d\\d\\.tif$')
      match = pattern.search(str(self.path))
      if not match:
        raise Exception("Cannot find Z position") 
      self._z = int(match[1])
    return self._z





def generate_maximum_projection_cli_str(source_image_prefix, destination):
  # TODO: not sure this file will be in the path in swarm. might need to configure the swarm env?
  return "pipenv run python %s %s %s" % (__file__, source_image_prefix, destination)

@cli.log.LoggingApp
def generate_maximum_projection_cli(app):
  try:
    GenerateMaximumProjectionJob(
      app.params.source_image_prefix,
      app.params.destination
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_maximum_projection_cli.add_param("source_image_prefix")
generate_maximum_projection_cli.add_param("destination")

if __name__ == "__main__":
  #  generate_maximum_projection_cli.run()
  try:
    GenerateMaximumProjectionJob(
      "C:\\Users\\finne\\Desktop\\hesc-chr1-fish-btoa_20201230_183248\\Plate1_12-30-20_18-38-45\\",
      "Plate1_12-30-20_18-38-45_B02_T0001F001L01A02Z??C01.tif",
      "C:\\Users\\finne\\Desktop\\output\\"
    ).run()
  except Exception as exception:
    traceback.print_exc()
