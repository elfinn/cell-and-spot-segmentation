import re
import logging
import os
from models.image_name_dictionaries.image_filename_CV import CVImageFilename
from models.image_name_dictionaries.image_filename_LSM import LSMImageFilename

LOGGER = logging.getLogger()

FILE_TYPE = os.environ.get('FILE_TYPE')





class ImageFilename:
  @classmethod
  def parse(cls, image_filename_str):
    if FILE_TYPE == 'CV':
        return CVImageFilename.parse(image_filename_str)
    elif FILE_TYPE == 'LSM':
        return LSMImageFilename.parse(image_filename_str)

  def __init__(self):
    if FILE_TYPE == 'CV':
        return CVImageFilename(experiment, well, t, f, l, a, z, c, suffix, extension)
    elif FILE_TYPE == 'LSM':
        return LSMImageFilename(experiment, well, timestamp, z, c, suffix, extension)

  def __str__(self):
    if FILE_TYPE == 'CV':
        return str(CVImageFilename(self))
    elif FILE_TYPE == 'LSM':
        return str(LSMImageFilename(self))

  def __copy__(self):
    if FILE_TYPE == 'CV':
        return CVImageFilename.__copy__(self)
    elif FILE_TYPE == 'LSM':
        return LSMImageFilename.__copy__(self)
