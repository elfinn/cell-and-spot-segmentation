import numpy
import skimage.io

from models.image_filename import ImageFilename


class ZSlicedImage:
  def __init__(self, path, source):
    self.path = path
    self.source_dir = source

  @property
  def image(self):
    if not hasattr(self, "_image"):
      self._image = skimage.io.imread(self.path, as_gray=True)
    return self._image

  @property
  def z(self):
    if not hasattr(self, "_z"):
      image_filename = ImageFilename.parse(str(self.path.relative_to(self.source_dir)))
      self._z = image_filename.z
    return self._z
