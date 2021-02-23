import traceback
from datetime import datetime
import cli.log
import logging

from generate_spot_result_line import generate_spot_result_line_cli_str

from models.paths import *
from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob
from models.swarm_job import SwarmJob, shard_job_params

SWARM_SUBJOBS_COUNT = 5

class GenerateAllSpotResultLinesJob:
  def __init__(
    self,
    spots_source_directory,
    z_centers_source_directory,
    distance_transforms_source_directory,
    nuclear_masks_source_directory_path,
    destination
  ):
    self.spots_source_directory = spots_source_directory
    self.z_centers_source_directory = z_centers_source_directory
    self.distance_transforms_source_directory = distance_transforms_source_directory
    self.nuclear_masks_source_directory_path = nuclear_masks_source_directory_path
    self.destination = destination
    self.logger = logging.getLogger()
  
  def run(self):
    SwarmJob(
      self.destination,
      self.job_name,
      self.jobs,
      SWARM_SUBJOBS_COUNT
    ).run()

  @property
  def jobs(self):
    if not hasattr(self, "_jobs"):
      spot_source_paths_shards = shard_job_params(self.spot_source_paths, SWARM_SUBJOBS_COUNT)
      self._jobs = [
        generate_spot_result_line_cli_str(
          spot_source_paths_shard,
          self.z_centers_source_directory,
          self.distance_transforms_source_directory,
          self.nuclear_masks_source_directory_path,
          self.destination
        )
        for spot_source_paths_shard in spot_source_paths_shards
      ]
    return self._jobs

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_spot_result_lines_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name
  
  @property
  def spots_source_directory_path(self):
    if not hasattr(self, "_spots_source_directory_path"):
      self._spots_source_directory_path = source_path(self.spots_source_directory)
      if not self._spots_source_directory_path.is_dir():
        raise Exception("spots source directory does not exist")
    return self._spots_source_directory_path

  @property
  def spot_source_paths(self):
    return self.spots_source_directory_path.glob(str(ImageFilenameGlob(suffix="_nucleus_???_spot_*", extension="npy")))

@cli.log.LoggingApp
def generate_all_spot_result_lines_cli(app):
  try:
    GenerateAllSpotResultLinesJob(
      app.params.spots_source_directory,
      app.params.z_centers_source_directory,
      app.params.distance_transforms_source_directory,
      app.params.nuclear_masks_source_directory_path,
      app.params.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_spot_result_lines_cli.add_param("spots_source_directory", default="todo", nargs="?")
generate_all_spot_result_lines_cli.add_param("z_centers_source_directory", default="todo", nargs="?")
generate_all_spot_result_lines_cli.add_param("distance_transforms_source_directory", default="todo", nargs="?")
generate_all_spot_result_lines_cli.add_param("nuclear_masks_source_directory_path", default="todo", nargs="?")
generate_all_spot_result_lines_cli.add_param("destination", default="C:\\\\Users\\finne\\Documents\\python\\spot_result_lines\\", nargs="?")

if __name__ == "__main__":
   generate_all_spot_result_lines_cli.run()
