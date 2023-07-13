import logging
import traceback
from datetime import datetime

import argparse

from generate_cropped_cell_image import generate_cropped_cell_image_cli_str
from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob
from models.paths import *
from models.swarm_job import shard_job_params, SwarmJob

FILES_PER_CALL_COUNT = 20000
MEMORY = 1.5

LOGGER = logging.getLogger()
class GenerateAllCroppedCellImagesJob:
  def __init__(self, source_images, source_masks, destination, log, DAPI_channel):
    self.source_images = source_images
    self.source_masks = source_masks
    self.destination = destination
    self.logdir = log
    self.logger = logging.getLogger()
    self.DAPI_channel = DAPI_channel
  
  def run(self):
    SwarmJob(
      self.source_images,
      self.destination_path,
      self.job_name,
      self.file_dictionary,
      self.cli_str,
      self.logdir,
      MEMORY,
      FILES_PER_CALL_COUNT
    ).run()

  @property
  def cli_str(self):
    if not hasattr(self, "_cli_str"):
      self._cli_str = generate_cropped_cell_image_cli_str(self.destination_path, self.source_images, self.source_masks)
    return self._cli_str

  @property
  def pairs(self):
    if not hasattr(self, "_pairs"):
      self._pairs = [
        (source_image_path, source_mask_path)
        for source_image_path in self.source_image_paths
        for source_mask_path in self.source_mask_paths_for_source_image_path(source_image_path)
      ]
    return self._pairs

  @property
  def file_dictionary(self):
    if hasattr(self, "_file_dictionary"): 
        raise Exception("filename dictionaries already processed")
    self._file_dictionary = self.destination_path / "input_file_dictionary.txt"
    LOGGER.warning("Generating file dictionary (this can take a while)")
    with self._file_dictionary.open("w") as file_dictionary:
        for tuple in self.pairs:
          file_dictionary.write("%s;%s\n"%(str(tuple[0]), str(tuple[1])))    
    return self._file_dictionary

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "crop_%s" % datetime.now().strftime("%y%m%d%H%M%S")
    return self._job_name
  
  @property
  def source_images_path(self):
    if not hasattr(self, "_source_images_path"):
      self._source_images_path = source_path(self.source_images)
    return self._source_images_path

  @property
  def source_masks_path(self):
    if not hasattr(self, "_source_masks_path"):
      self._source_masks_path = source_path(self.source_masks)
    return self._source_masks_path
  
  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path
  
  @property
  def source_image_paths(self):
    if not hasattr(self, "_source_image_paths"):
      self._source_image_paths = [
        image_file_path
        for image_file_path
        in self.source_images_path.rglob(str(ImageFilenameGlob(suffix="_maximum_projection", extension="tif")))
        if ImageFilename.parse(str(image_file_path.relative_to(self.source_images_path))).c != self.DAPI_channel
      ] + [
        z_center_file_path
        for z_center_file_path
        in self.source_images_path.rglob(str(ImageFilenameGlob(suffix="_z_center", extension="npy")))
        if ImageFilename.parse(str(z_center_file_path.relative_to(self.source_images_path))).c != self.DAPI_channel
      ]
    return self._source_image_paths

  def source_mask_paths_for_source_image_path(self, source_image_path):
    source_image_filename = ImageFilename.parse(str(source_image_path.relative_to(self.source_images_path)))
    source_mask_filename_glob = ImageFilenameGlob.from_image_filename(source_image_filename, excluding_keys=["a", "c", "z"])
    source_mask_filename_glob.glob.suffix = "_nucleus_???"
    source_mask_filename_glob.glob.extension = "npy"
    return self.source_masks_path.rglob(str(source_mask_filename_glob))

parser = argparse.ArgumentParser()
parser.add_argument("source_images")
parser.add_argument("source_masks")
parser.add_argument("destination")

def generate_all_cropped_cell_images_cli(parser):
  args = parser.parse_args()
  try:
    GenerateAllCroppedCellImagesJob(
      args.source_images,
      args.source_masks,
      args.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
   generate_all_cropped_cell_images_cli(parser)
