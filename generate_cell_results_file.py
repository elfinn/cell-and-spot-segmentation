import traceback

import argparse

from models.image_filename import ImageFilename
from models.image_filename_glob import ImageFilenameGlob
from models.paths import *


class GenerateCellResultsFileJob:
  def __init__(self, source, destination, prefix):
    self.source = source
    self.destination = destination
    self.prefix = prefix

  def run(self):
    with open(self.destination_filename, 'w') as destination_file:
      destination_file.write(self.headers)
      for result_line_path in self.result_line_paths:
        with open(result_line_path) as result_line_file:
          next(result_line_file)
          for line in result_line_file:
            if not line.isspace():
              destination_file.write(line)

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
      if not self._source_path.is_dir():
        raise Exception("source directory does not exist")
    return self._source_path

  @property
  def result_line_paths(self):
    return self.source_path.rglob(str(ImageFilenameGlob(suffix="_summed_intensity_nucleus_???", extension="csv")))
  
  @property
  def arbitrary_result_line_path(self):
    if not hasattr(self, "_arbitrary_result_line_path"):
      self._arbitrary_result_line_path = next(self.result_line_paths)
    return self._arbitrary_result_line_path
  
  @property
  def arbitrary_result_line_image_filename(self):
    if not hasattr(self, "_arbitrary_result_line_image_filename"):
      self._arbitrary_result_line_image_filename = ImageFilename.parse(str(self.arbitrary_result_line_path.relative_to(self.source_path)))
    return self._arbitrary_result_line_image_filename

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def destination_filename(self):
    if not hasattr(self, "_destination_filename"):
      self._destination_filename = self.destination_path / ("%s_cell_intensities.csv" % self.prefix)
    return self._destination_filename
  
  @property
  def headers(self):
    if not hasattr(self, "_headers"):
      with open(self.arbitrary_result_line_path) as artibrary_result_line_file:
        self._headers = next(artibrary_result_line_file)
    return self._headers

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")

def generate_cell_results_file_cli(parser):
  args = parser.parse_args()
  try:
    GenerateCellResultsFileJob(
      args.source,
      args.destination,
    ).run()
  except Exception as exception:
    traceback.print_exc()

if __name__ == "__main__":
   generate_cell_results_file_cli(parser)
