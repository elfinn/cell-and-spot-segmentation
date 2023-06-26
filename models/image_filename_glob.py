import os
from models.image_name_dictionaries.image_filename_glob_IMX import IMXImageFilenameGlob
from models.image_name_dictionaries.image_filename_glob_LSM import LSMImageFilenameGlob

IMAGE_FILETYPE = os.environ.get('FILE_TYPE')

if IMAGE_FILETYPE == 'LSM':
   IMAGE_FILENAME_KEYS = set([
     "date",
     "position",
     "group",
     "f",
     "c",
     "z",
     "suffix",
     "extension"
   ])
elif IMAGE_FILETYPE == 'IMX':
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

class ImageFilenameGlob:
    image_filetype = os.environ.get('FILE_TYPE')
    
    @classmethod
    def from_image_filename(cls, image_filename, excluding_keys=[]):
        keys = IMAGE_FILENAME_KEYS - set(excluding_keys)
        return cls(**{ key: getattr(image_filename, key) for key in keys })

    def __init__(self, date=None, project=None, position=None, group=None, f=None, z=None, c=None, suffix=None, extension=None):
        if IMAGE_FILETYPE == 'LSM':
            self.glob = LSMImageFilenameGlob(date, position, group, f, z, c, suffix, extension)
        elif IMAGE_FILETYPE == 'IMX':
            self.glob = IMXImageFilenameGlob(date, group, project, position, f, c, suffix, extension)
            
    def __str__(self):
      if IMAGE_FILETYPE == 'LSM':
        return str(self.glob)
      elif IMAGE_FILETYPE == 'IMX':
        return str(self.glob)

    def __hash__(self):
      if IMAGE_FILETYPE == 'LSM':
        return hash(self.glob)
      elif IMAGE_FILETYPE == 'IMX':
        return hash(self.glob)
    
    def __eq__(self, other):
      if IMAGE_FILETYPE == 'LSM':
        return LSMImageFilenameGlob.__eq__(self.glob,other.glob)
      elif IMAGE_FILETYPE == 'IMX':
        return IMXImageFilenameGlob.__eq__(self.glob,other.glob)
