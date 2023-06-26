IMAGE_FILENAME_KEYS = set([
     "date",
     "group",
     "project",
     "position",
     "f",
     "c",
     "suffix",
     "extension"
  ])

class IMXImageFilenameGlob:
  @classmethod
  def from_image_filename(cls, image_filename, excluding_keys=[]):
    keys = IMAGE_FILENAME_KEYS - set(excluding_keys)
    return cls(**{ key: getattr(image_filename, key) for key in keys })

  def __init__(self, date=None, group=None, project=None, position=None, f=None, c=None, suffix=None, extension=None):
    self.date = date
    self.group = group
    self.project = project
    self.position = position
    self.f = f
    self.c = c
    self.suffix = suffix
    self.extension = extension

  def __str__(self):
    return  ("%s/%s/%s_%s_s%s_w%s%s.%s" % (
      self.date_glob,
      self.group_glob,
      self.project_glob,
      self.position_glob,
      self.f_glob,
      self.c_glob,
      self.suffix_glob,
      self.extension_glob
    ))

  def __hash__(self):
    return hash((self.date, self.group, self.project, self.position, self.f, self.c, self.suffix, self.extension))

  def __eq__(self, other):
    return (
      isinstance(other, IMXImageFilenameGlob) and
      self.date == other.date and
      self.group == other.group and
      self.project == other.project and
      self.position == other.position and
      self.c == other.c and
      self.suffix == other.suffix and
      self.extension == other.extension
    )

  @property
  def date_glob(self):
    if self.date != None:
      return self.date
    else:
      return "????-??-??"

  @property
  def group_glob(self):
    if self.group != None:
      return self.group
    else:
      return "???"

  @property
  def project_glob(self):
    if self.project != None:
      return self.project
    else:
      return "*"

  @property
  def position_glob(self):
    if self.position != None:
      return self.position
    else:
      return "???"

  @property
  def f_glob(self):
    if self.f != None:
      return "%i" % self.f
    else:
      return "?"

  @property
  def c_glob(self):
    if self.c != None:
      return "%i" % self.c
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
