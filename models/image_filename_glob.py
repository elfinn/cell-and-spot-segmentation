import os
from image_name_dictionaries.image_filename_glob_CV import CVImageFilenameGlob
from image_name_dictionaries.image_filename_glob_LSM import LSMImageFilenameGlob

IMAGE_FILETYPE = os.environ.get('FILE_TYPE')

if IMAGE_FILETYPE == 'CV':
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
elif IMAGE_FILETYPE == 'LSM':
   IMAGE_FILENAME_KEYS = set([
     "experiment",
     "well",
     "timepoint",
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

  def __init__(self, experiment=None, well=None, timepoint=None, t=None, f=None, l=None, a=None, z=None, c=None, suffix=None, extension=None):
    if IMAGE_FILETYPE == 'CV':
        self = CVImageFilenamesGlob(experiment, well, t, f, l, a, z, c, suffix, extension)
    elif IMAGE_FILETYPE == 'LSM':
        self = LSMImageFilenamesGlob(experiment, well, timepoint, f, z, c, suffix, extension)

  def __str__(self):
    return self.to_glob()

  def to_glob(self):
    if IMAGE_FILETYPE == 'CV':
        return CVImageFilenamesGlob.to_glob(self)
    elif IMAGE_FILETYPE == 'LSM':
        return LSMImageFilenamesGlob.to_glob(self)

  def __hash__(self):
    if IMAGE_FILETYPE == 'CV':
        return hash((self.experiment, self.well, self.t, self.f, self.l, self.a, self.z, self.c, self.suffix, self.extension))
    elif IMAGE_FILETYPE == 'LSM':
        return hash(self.experiment, self.well, self.timepoint, self.f, self.z, self.c, self.suffix, self.extension)
    
  def __eq__(self, other):
    if IMAGE_FILETYPE == 'CV':
        return(CVImageFilenameGlob(self) == CVImageFilenameGlob(other))
    if IMAGE_FILETYPE == 'LSM':
        return(LSMImageFilenameGlob(self) == LSMImageFilenameGlob(other))
