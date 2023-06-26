import re
import logging
import os
from models.image_name_dictionaries.image_filename_LSM import LSMImageFilename
from models.image_name_dictionaries.image_filename_IMX import IMXImageFilename

LOGGER = logging.getLogger()

FILE_TYPE = os.environ.get('FILE_TYPE')

class ImageFilename:
  @classmethod
  def parse(cls, image_filename_str):
    if  FILE_TYPE == 'LSM':
        return LSMImageFilename.parse(image_filename_str)
    elif FILE_TYPE == 'IMX':
        return IMXImageFilename.parse(image_filename_str)

  def __init__(self):
    if FILE_TYPE == 'LSM':
        self.glob = LSMImageFilename(date, position, track, f, z, c, suffix, extension)
    elif FILE_TYPE == 'IMX':
        self.glob = IMXImageFilename(date, plate, project, position, f, c, suffix, extension)

  def __str__(self):
    if FILE_TYPE == 'LSM':
        return str(self.glob)
    elif FILE_TYPE == 'IMX':
        return str(self.glob)

  def __copy__(self):
    if FILE_TYPE == 'LSM':
        return LSMImageFilename.__copy__(self.glob)
    elif FILE_TYPE == 'IMX':
        return IMXImageFilename.__copy__(self.glob)
