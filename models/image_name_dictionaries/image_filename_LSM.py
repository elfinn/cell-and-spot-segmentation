import re
import logging

LOGGER = logging.getLogger()


IMAGE_FILE_RE = re.compile( 
    "(?P<date>\\d{8})/" +
    "CS(?P<position>\\d{1})/" +
    "(?P<group>.+)/" +
    "p(?P<f>\\d{1,2}|XX)/" +
    "ch(?P<c>\\d{1}|XX)/" +
    "z(?P<z>\\d{1,2}|XX)"+
    "(?P<suffix>.*)" +
    "\." + 
    "(?P<extension>.+)"
  )

class LSMImageFilename:
  @classmethod
  def parse(cls, image_filename_str):
    match = IMAGE_FILE_RE.match(image_filename_str)
    if not match:
       raise Exception("invalid image filename: %s" % image_filename_str)
    return cls(
      date=match["date"],
      position=match["position"],
      group=match["group"],
      f=(None if match["f"] == "XXX" else int(match["f"])),
      z=(None if match["z"] == "XX" else int(match["z"])),
      c=(None if match["c"] == "XX" else int(match["c"])),
      suffix=match["suffix"],
      extension=match["extension"],
    )

  def __init__(self, date, position, group, f, z, c, suffix, extension):
    self.date = date
    self.position = position
    self.group = group
    self.f = f
    self.z = z
    self.c = c
    self.suffix = suffix
    self.extension = extension

  def __str__(self):
     return "%s/CS%s/%s/p%s/ch%s/z%s%s.%s" % (
       self.date,
       self.position,
       self.group,
       self.f_str,
       self.c_str,
       self.z_str,
       self.suffix,
       self.extension
     )

  def __copy__(self):
    return LSMImageFilename(
      date=self.date,
      position=self.position,
      group=self.group,
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
    return "XX" if not self.z else ("%i" % self.z)

  @property
  def c_str(self):
    return "XX" if not self.c else ("%i" % self.c)
