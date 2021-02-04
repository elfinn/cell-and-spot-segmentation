IMAGE_FILENAME_KEYS = set([
  "experiment",
  "well",
  "t",
  "f",
  "l",
  "a",
  "z",
  "c"
])

class ImageFilenameConstraint:
  @classmethod
  def from_image_filename(cls, image_filename, excluding_keys=[]):
    keys = IMAGE_FILENAME_KEYS - set(excluding_keys)
    return cls(**{ key: getattr(image_filename, key) for key in keys })

  def __init__(self, experiment=None, well=None, t=None, f=None, l=None, a=None, z=None, c=None):
    self.experiment = experiment
    self.well = well
    self.t = t
    self.f = f
    self.l = l
    self.a = a
    self.z = z
    self.c = c

  def __str__(self):
    return "%s_%s_T%sF%sL%sA%sZ%sC%s.tif" % (
      self.experiment,
      self.well,
      self.t_str,
      self.f_str,
      self.l_str,
      self.a_str,
      self.z_str,
      self.c_str
    )
  
  def __hash__(self):
    return hash((self.experiment, self.well, self.t, self.f, self.l, self.a, self.z, self.c))

  def __eq__(self, other):
    return (
      isinstance(other, ImageFilenameConstraint) and
      self.experiment == other.experiment and
      self.well == other.well and
      self.t == other.t and
      self.f == other.f and
      self.l == other.l and
      self.a == other.a and
      self.z == other.z and
      self.c == other.c
    )

  @property
  def t_str(self):
    if self.t:
      return "%04i" % self.t
    else:
      return "?" * 4

  @property
  def f_str(self):
    if self.f:
      return "%03i" % self.f
    else:
      return "?" * 3

  @property
  def l_str(self):
    if self.l:
      return "%02i" % self.l
    else:
      return "?" * 2

  @property
  def a_str(self):
    if self.a:
      return "%02i" % self.a
    else:
      return "?" * 2

  @property
  def z_str(self):
    if self.z:
      return "%02i" % self.z
    else:
      return "?" * 2

  @property
  def c_str(self):
    if self.c:
      return "%02i" % self.c
    else:
      return "?" * 2
