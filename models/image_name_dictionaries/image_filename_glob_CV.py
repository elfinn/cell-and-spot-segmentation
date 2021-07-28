IMAGE_FILENAME_KEYS = set([
  "experiment",
  "well",
  "t",
  "f",
  "l",
  "a",
  "z",
  "c",
  "suffix",
  "extension"
])

class CVImageFilenameGlob:
  @classmethod
  def from_image_filename(cls, image_filename, excluding_keys=[]):
    keys = IMAGE_FILENAME_KEYS - set(excluding_keys)
    return cls(**{ key: getattr(image_filename, key) for key in keys })

  def __init__(self, experiment=None, well=None, t=None, f=None, l=None, a=None, z=None, c=None, suffix=None, extension=None):
    self.experiment = experiment
    self.well = well
    self.t = t
    self.f = f
    self.l = l
    self.a = a
    self.z = z
    self.c = c
    self.suffix = suffix
    self.extension = extension

  def __str__(self):
    return self.to_glob()

  def to_glob(self):
    return  ("%s_%s_T%sF%sL%sA%sZ%sC%s%s.%s" % (
      self.experiment_glob,
      self.well_glob,
      self.t_glob,
      self.f_glob,
      self.l_glob,
      self.a_glob,
      self.z_glob,
      self.c_glob,
      self.suffix_glob,
      self.extension_glob
    ))

  def __hash__(self):
    return hash((self.experiment, self.well, self.t, self.f, self.l, self.a, self.z, self.c, self.suffix, self.extension))

  def __eq__(self, other):
    return (
      isinstance(other, ImageFilenameGlob) and
      self.experiment == other.experiment and
      self.well == other.well and
      self.t == other.t and
      self.f == other.f and
      self.l == other.l and
      self.a == other.a and
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
      return "?" * 3

  @property
  def t_glob(self):
    if self.t != None:
      return "%04i" % self.t
    else:
      return "?" * 4

  @property
  def f_glob(self):
    if self.f != None:
      return "%03i" % self.f
    else:
      return "?" * 3

  @property
  def l_glob(self):
    if self.l != None:
      return "%02i" % self.l
    else:
      return "?" * 2

  @property
  def a_glob(self):
    if self.a != None:
      return "%02i" % self.a
    else:
      return "?" * 2

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
      return "?" * 2

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
