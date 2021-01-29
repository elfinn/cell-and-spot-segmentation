import traceback
from datetime import datetime
from pathlib import Path
import cli.log
import logging
from generate_maximum_projection import generate_maximum_projection_cli_str
import subprocess
from time import sleep

class GenerateAllMaximumProjectionsJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination
    self.job_name = "generate_all_maximum_projections_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    self.logger = logging.getLogger()
  
  def start(self):
    self.generate_swarm_file()
    self.submit_swarm_job()
    while not self.is_swarm_job_complete():
      sleep(5)

  def generate_swarm_file(self):
    with self.swarm_file_path.open("w") as swarm_file:
        for image_file in self.source_path.glob("*.c01.tiff"):
          swarm_file.write("%s\n" % generate_maximum_projection_cli_str(image_file, self.destination))
  
  def submit_swarm_job(self):
    subprocess.run("swarm -f %s --job-name %s" % (self.swarm_file_path, self.job_name)).check_returncode()

  def is_swarm_job_complete(self):
    sjobs_result = subprocess.run("squeue -n %s -o \"%T\"" % self.job_name)
    sjobs_result.check_returncode()
    # heavy assumptions here:
    # - sjobs will only include our one job line, no others
    # - sjobs will return our line when it's completed
    # - sjobs outputs to stdout
    return sjobs_result.stdout.find("COMPLETED") != -1

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

@cli.log.LoggingApp
def generate_all_maximum_projections_cli(app):
  try:
    GenerateAllMaximumProjectionsJob(
      app.params.source,
      app.params.destination
    ).start()
  except Exception as exception:
    traceback.print_exc()

generate_all_maximum_projections_cli.add_param("source")
generate_all_maximum_projections_cli.add_param("destination")

if __name__ == "__main__":
  generate_all_maximum_projections_cli.run()
