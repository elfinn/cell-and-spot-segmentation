import re
import logging

LOGGER = logging.getLogger()

CV_IMAGE_FILE_RE = re.compile(
    "(?P<experiment>.+)" + 
    "_" + 
    "(?P<well>[A-Z]\\d{2})" +
    "_" +
    "T(?P<t>\\d{4}|XXXX)" +
    "F(?P<f>\\d{3}|XXX)" +
    "L(?P<l>\\d{2}|XX)" +
    "A(?P<a>\\d{2}|XX)" + 
    "Z(?P<z>\\d{2}|XX)" + 
    "C(?P<c>\\d{2}|XX)" + 
    "(?P<suffix>.*)" + 
    "\\." + 
    "(?P<extension>.+)"
  )

LSM_IMAGE_FILE_RE = re.compile(
    "(?P<experiment>.+)" + 
    "\\" + 
    "(?P<well>[A-Za-z0-9]+)" +
    "_\\d{4}_\\d{2}_\\d{2}__\\d{2}_\\d{2}_\\d{2}\\" +
    "p(?P<f>\\d{1,3}|XXX)\\" +
    "ch(?P<c>\\d{1}|XX)\\" + 
    "z(?P<z>\\d{2}|XX)" + 
    "\\." + 
    "(?P<extension>.+)"
  )

class ImageFilename:
  @classmethod
  def parse(cls, image_filename_str):
    match = CV_IMAGE_FILE_RE.match(image_filename_str)
    if not match:
      match = LSM_IMAGE_FILE_RE.match(image_filename_str)
      if not match:
        raise Exception("invalid image filename: %s" % image_filename_str)
    return cls(
      experiment=match["experiment"],
      well=match["well"],
      t=(None if match["t"] == "XXXX" else int(match["t"])),
      f=(None if match["f"] == "XXX" else int(match["f"])),
      l=(None if match["l"] == "XX" else int(match["l"])),
      a=(None if match["a"] == "XX" else int(match["a"])),
      z=(None if match["z"] == "XX" else int(match["z"])),
      c=(None if match["c"] == "XX" else int(match["c"])),
      suffix=match["suffix"],
      extension=match["extension"],
    )

  def __init__(self, experiment, well, t, f, l, a, z, c, suffix, extension):
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
    return "%s_%s_T%sF%sL%sA%sZ%sC%s%s.%s" % (
      self.experiment,
      self.well,
      self.t_str,
      self.f_str,
      self.l_str,
      self.a_str,
      self.z_str,
      self.c_str,
      self.suffix,
      self.extension
    )

  def __copy__(self):
    return ImageFilename(
      experiment=self.experiment,
      well=self.well,
      t=self.t,
      f=self.f,
      l=self.l,
      a=self.a,
      z=self.z,
      c=self.c,
      suffix=self.suffix,
      extension=self.extension
    )

  @property
  def t_str(self):
    return "XXXX" if not self.t else ("%04i" % self.t)

  @property
  def f_str(self):
    return "XXX" if not self.f else ("%03i" % self.f)

  @property
  def l_str(self):
    return "XX" if not self.l else ("%02i" % self.l)

  @property
  def a_str(self):
    return "XX" if not self.a else ("%02i" % self.a)

  @property
  def z_str(self):
    return "XX" if not self.z else ("%02i" % self.z)

  @property
  def c_str(self):
    return "XX" if not self.c else ("%02i" % self.c)
