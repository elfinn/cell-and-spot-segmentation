IMAGE_FILENAME_KEYS = set([
  "experiment",
  "well",
  "timestamp",
  "f",
  "z",
  "c",
  "suffix",
  "extension"
])

class ImageFilenameGlob:
  @classmethod
  def from_image_filename(cls, image_filename, excluding_keys=[]):
    keys = IMAGE_FILENAME_KEYS - set(excluding_keys)
    return cls(**{ key: getattr(image_filename, key) for key in keys })

  def __init__(self, experiment=None, well=None, timestamp=None, f=None, z=None, c=None, suffix=None, extension=None):
    self.experiment = experiment
    self.well = well
    self.timestamp = timestamp
    self.f = f
    self.z = z
    self.c = c
    self.suffix = suffix
    self.extension = extension

  def __str__(self):
    return self.to_glob()

  def to_glob(self):
    return  ("%s/%s_%s/p%s/ch%s/z%s%s.%s" % (
      self.experiment_glob,
      self.well_glob,
      self.timestamp_glob,
      self.f_glob,
      self.c_glob,
      self.z_glob,
      self.suffix_glob,
      self.extension_glob
    ))

  def __hash__(self):
    return hash((self.experiment, self.well, self.timestamp, self.f, self.z, self.c, self.suffix, self.extension))

  def __eq__(self, other):
    return (
      isinstance(other, ImageFilenameGlob) and
      self.experiment == other.experiment and
      self.well == other.well and
      self.timestamp == other.timestamp and
      self.f == other.f and
      self.z == other.z and
      self.c == other.c and
      self.suffix == other.suffix and
      self.extension == other.extension
    )

  @property
  def experiment_glob(self):
    if self.experiment != None:
      return self.experiment
    else:
      return "*"

  @property
  def well_glob(self):
    if self.well != None:
      return self.well
    else:
      return "*"

  @property
  def timestamp_glob(self):
    if self.timestamp != None:
      return self.timestamp
    else:
      return "????_??_??__??_??_??"

  @property
  def f_glob(self):
    if self.f != None:
      return "%03i" % self.f
    else:
      return "*"

  @property
  def z_glob(self):
    if self.z != None:
      return "%02i" % self.z
    else:
      return "?" * 2

  @property
  def c_glob(self):
    if self.c != None:
      return "%02i" % self.c
    else:
      return "?"

  @property
  def suffix_glob(self):
    if self.suffix != None:
      return self.suffix
    else:
      return "*"

  @property
  def extension_glob(self):
    if self.extension != None:
      return self.extension
    else:
      return "*"
