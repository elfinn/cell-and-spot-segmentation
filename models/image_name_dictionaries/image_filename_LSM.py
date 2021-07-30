import re
import logging

LOGGER = logging.getLogger()





IMAGE_FILE_RE = re.compile(
    "(?P<experiment>.+)" + 
    "/" + 
    "(?P<well>[A-Za-z0-9]+)" +
    "_(?P<timestamp>\\d{4}_\\d{2}_\\d{2}__\\d{2}_\\d{2}_\\d{2})/" +
    "p(?P<f>\\d{1,3}|XXX)/" +
    "ch(?P<c>\\d{1}|XX)/" + 
    "z(?P<z>\\d{2}|XX)" +
    "(?P<suffix>.*)" +
    "\\." + 
    "(?P<extension>.+)"
  )

class LSMImageFilename:
  @classmethod
  def parse(cls, image_filename_str):
    match = IMAGE_FILE_RE.match(image_filename_str)
    if not match:
       raise Exception("invalid image filename: %s" % image_filename_str)
    return cls(
      experiment=match["experiment"],
      well=match["well"],
      timestamp=match["timestamp"],
      f=(None if match["f"] == "XXX" else int(match["f"])),
      z=(None if match["z"] == "XX" else int(match["z"])),
      c=(None if match["c"] == "XX" else int(match["c"])),
      suffix=match["suffix"],
      extension=match["extension"],
    )

  def __init__(self, experiment, well, timestamp, f, z, c, suffix, extension):
    self.experiment = experiment
    self.well = well
    self.timestamp = timestamp
    self.f = f
    self.z = z
    self.c = c
    self.suffix = suffix
    self.extension = extension

  def __str__(self):
     return "%s/%s_%s/p%s/ch%s/z%s%s.%s" % (
       self.experiment,
       self.well,
       self.timestamp,
       self.f_str,
       self.c_str,
       self.z_str,
       self.suffix,
       self.extension
     )

  def __copy__(self):
    return ImageFilename(
      experiment=self.experiment,
      well=self.well,
      timestamp=self.timestamp,
      f=self.f,
      z=self.z,
      c=self.c,
      suffix=self.suffix,
      extension=self.extension
    )

  @property
  def f_str(self):
    return "XXX" if not self.f else ("%i" % self.f)

  @property
  def z_str(self):
    return "XX" if not self.z else ("%02i" % self.z)

  @property
  def c_str(self):
    return "XX" if not self.c else ("%i" % self.c)
