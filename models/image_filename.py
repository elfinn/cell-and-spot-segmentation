import re
import logging

IMAGE_FILE_RE = re.compile(
    "(?P<experiment>.+)" + 
    "_" + 
    "(?P<well>[A-Z]\\d{2})" +
    "_" +
    "T(?P<t>\\d{4})" +
    "F(?P<f>\\d{3})" +
    "L(?P<l>\\d{2})" +
    "A(?P<a>\\d{2})" + 
    "Z(?P<z>\\d{2}|XX)" + 
    "C(?P<c>\\d{2})" + 
    "(?P<suffix>.*)" + 
    "\\." + 
    "(?P<extension>.+)"
  )

class ImageFilename:
  def __init__(self, image_filename_str):
    self.image_filename_str = image_filename_str

  def __str__(self):
    return self.image_filename_str

  @property
  def experiment(self):
    return self.match["experiment"]

  @property
  def well(self):
    return self.match["well"]

  @property
  def t(self):
    return int(self.match["t"])

  @property
  def f(self):
    return int(self.match["f"])

  @property
  def l(self):
    return int(self.match["l"])

  @property
  def a(self):
    return int(self.match["a"])

  @property
  def z(self):
    if self.match["z"] == "XX":
      return None
    else:
      return int(self.match["z"])

  @property
  def c(self):
    return int(self.match["c"])

  @property
  def suffix(self):
    return self.match["suffix"]

  @property
  def extension(self):
    return self.match["extension"]

  @property
  def match(self):
    if not hasattr(self, '_match'):
        self._match = IMAGE_FILE_RE.match(self.image_filename_str)
        if not self._match:
          raise Exception("invalid image filename: %s" % self.image_filename_str)
    return self._match
