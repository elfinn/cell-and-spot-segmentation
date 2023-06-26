import re
import logging

LOGGER = logging.getLogger()

IMAGE_FILE_RE = re.compile( 
    "(?P<date>\\d{4}-\\d{2}-\\d{2})"+
    "/" +
    "(?P<group>\\d{3})" +
    "/" +
    "(?P<project>.*)" +
    "_(?P<position>[A-Z]\\d{2})" +
    "_s(?P<f>\\d{1,2}|X)" +
    "_w(?P<c>\\d{1}|X){0,1}"+
    "(?P<suffix>.*)" +
    "\." + 
    "(?P<extension>.+)"
  )

class IMXImageFilename:
  @classmethod
  def parse(cls, image_filename_str):
    match = IMAGE_FILE_RE.match(image_filename_str)
    if not match:
       raise Exception("invalid image filename: %s" % image_filename_str)
    return cls(
      date=match["date"],
      project=match["project"],
      group=match["group"],
      position=match["position"],
      f=(None if match["f"] == "X" else int(match["f"])),
      c=(None if match["c"] == "X" else int(match["c"])),
      suffix=match["suffix"],
      extension=match["extension"]
    )

  def __init__(self, date, project, group, position, f, c, suffix, extension):
    self.date = date
    self.project = project
    self.group = group
    self.position = position
    self.f = f
    self.c = c
    self.suffix = suffix
    self.extension = extension

  def __str__(self):
     return "%s/%s/%s_%s_s%s_w%s%s.%s" % (
       self.date,
       self.group,
       self.project,
       self.position,
       self.f_str,
       self.c_str,
       self.suffix,
       self.extension
     )

  def __copy__(self):
    return IMXImageFilename(
      date = self.date,
      group = self.group,
      project=self.project,
      position=self.position,
      f=self.f,
      c=self.c,
      suffix=self.suffix,
      extension=self.extension
    )

  @property
  def f_str(self):
    return "X" if not self.f else (self.f)

  @property
  def c_str(self):
    return "X" if not self.c else (self.c)
