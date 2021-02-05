import math
import traceback
from datetime import datetime
from pathlib import Path
import cli.log
import logging
from generate_maximum_projection import generate_maximum_projection_cli_str
import subprocess
from time import sleep
import re

from models.image_filename import *
from models.image_filename_constraint import *

class GenerateAllMaximumProjectionsJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination
    self.logger = logging.getLogger()
  
  def run(self):
    self.generate_swarm_file()
    self.start_swarm_job()
    while not self.is_swarm_job_complete():
      self.logger.warning("job not complete yet")
      sleep(5)
    self.logger.warning("complete")

  def generate_swarm_file(self):
    with self.swarm_file_path.open("w") as swarm_file:
      for image_filename_constraint in self.distinct_image_filename_constraints:
        swarm_file.write("%s\n" % generate_maximum_projection_cli_str(self.source, image_filename_constraint, self.destination))

  def start_swarm_job(self):
    command = [
      "swarm",
      "--module", "python/3.8",
      "-f", self.swarm_file_path,
      "--job-name", self.job_name,
      "-b", str(math.ceil(len(self.distinct_image_filename_constraints) / 5))
    ]
    self.logger.warning(command)
    subprocess.run(command).check_returncode()

  def is_swarm_job_complete(self):
    command = ["squeue", "-n", self.name, "-o", "\"%T\"", "-t", "all", "-h"]
    sjobs_result = subprocess.run(command, capture_output=True, text=True)
    self.logger.warning(command)
    sjobs_result.check_returncode()
    result_lines = sjobs_result.stdout.splitlines()
    self.logger.warning("squeue result: %s", sjobs_result.stdout)
    return (
      len(result_lines) == len(self.distinct_image_filename_constraints) and
      all((result_line == "COMPLETED" for result_line in result_lines))
    )

  @property
  def job_name(self):
    if not hasattr(self, "_job_name"):
      self._job_name = "generate_all_maximum_projections_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    return self._job_name
  
  @property
  def swarm_file_path(self):
    if not hasattr(self, "_swarm_file_path"):
      self._swarm_file_path = self.destination_path / "generate_all_maximum_projections.swarm"
    return self._swarm_file_path
  
  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = Path(self.source)
      if not self._source_path.is_dir():
        raise Exception("source does not exist")
    return self._source_path
  
  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = Path(self.destination)
      if not self._destination_path.exists():
        Path.mkdir(self._destination_path, parents=True)
      elif not self._destination_path.is_dir():
        raise Exception("destination already exists, but is not a directory")
    return self._destination_path
  
  @property
  def image_file_paths(self):
    return self.source_path.glob(IMAGE_FILE_GLOB)

  @property
  def image_filenames(self):
    return (ImageFilename(image_file_path.name) for image_file_path in self.image_file_paths)

  @property
  def distinct_image_filename_constraints(self):
    if not hasattr(self, "_distinct_image_filename_constraints"):
      self._distinct_image_filename_constraints = set((
        ImageFilenameConstraint.from_image_filename(image_filename, excluding_keys=["z"]) for image_filename in self.image_filenames
      ))
    return self._distinct_image_filename_constraints

@cli.log.LoggingApp
def generate_all_maximum_projections_cli(app):
  try:
    GenerateAllMaximumProjectionsJob(
      app.params.source,
      app.params.destination
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_all_maximum_projections_cli.add_param("source")
generate_all_maximum_projections_cli.add_param("destination")

if __name__ == "__main__":
  generate_all_maximum_projections_cli.run()
