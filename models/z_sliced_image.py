from PIL import Image
import numpy
from models.image_filename import ImageFilename

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
      image_filename = ImageFilename(self.path.name)
      self._z = image_filename.z
    return self._z
