import re

IMAGE_FILE_GLOB = "*_???_T????F???L??A??Z??C??.tif"

IMAGE_FILE_EXPERIMENT_PATTERN = "(?P<experiment>.+)"
IMAGE_FILE_WELL_PATTERN = "(?P<well>[A-Z]\\d{2})"
IMAGE_FILE_T_PATTERN = "T(?P<T>\\d{4})"
IMAGE_FILE_F_PATTERN = "F(?P<F>\\d{3})"
IMAGE_FILE_L_PATTERN = "L(?P<L>\\d{2})"
IMAGE_FILE_A_PATTERN = "A(?P<A>\\d{2})"
IMAGE_FILE_Z_PATTERN = "Z(?P<Z>\\d{2})"
IMAGE_FILE_C_PATTERN = "C(?P<C>\\d{2})"

IMAGE_FILE_PATTERN = (
  "%s_%s_%s%s%s%s%s%s\\.tif" % (
    IMAGE_FILE_EXPERIMENT_PATTERN, 
    IMAGE_FILE_WELL_PATTERN, 
    IMAGE_FILE_T_PATTERN, 
    IMAGE_FILE_F_PATTERN, 
    IMAGE_FILE_L_PATTERN, 
    IMAGE_FILE_A_PATTERN, 
    IMAGE_FILE_Z_PATTERN, 
    IMAGE_FILE_C_PATTERN
  )
)

IMAGE_FILE_RE = re.compile(IMAGE_FILE_PATTERN)

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
    return int(self.match["T"])

  @property
  def f(self):
    return int(self.match["F"])

  @property
  def l(self):
    return int(self.match["L"])

  @property
  def a(self):
    return int(self.match["A"])

  @property
  def z(self):
    return int(self.match["Z"])

  @property
  def c(self):
    return int(self.match["C"])

  @property
  def match(self):
    if not hasattr(self, '_match'):
        self._match = IMAGE_FILE_RE.match(self.image_filename_str)
        if not self._match:
          raise Exception("invalid image filename: %s" % self.image_filename_str)
    return self._match
