import shlex
import traceback

import cli.log
import numpy
import skimage.measure

from models.nuclear_mask import NuclearMask
from models.paths import *


class GenerateNuclearMasksJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination

  def run(self):
    for index, nuclear_mask in enumerate(self.nuclear_masks):
      numpy.save(self.indexed_destination_filename(index + 1), nuclear_mask)

  def indexed_destination_filename(self, index):
    return self.destination_path / self.source_path.stem.replace("_nuclear_segmentation", ("_nuclear_mask_%03i" % index))

  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path

  @property
  def segmentation(self):
    if not hasattr(self, "_segmentation"):
      self._segmentation = numpy.load(self.source_path, allow_pickle=True)
    return self._segmentation

  @property
  def regionprops(self):
    if not hasattr(self, "_regionprops"):
      self._regionprops = skimage.measure.regionprops(self.segmentation)
    return self._regionprops

  @property
  def nuclear_masks(self):
    if not hasattr(self, "_nuclear_masks"):
      self._nuclear_masks = [
        NuclearMask.build(self.segmentation, rp) for rp in self.regionprops
      ]
    return self._nuclear_masks

def generate_nuclear_masks_cli_str(sources, destination):
  return shlex.join([
    "pipenv",
    "run",
    "python",
    __file__,
    "--destination=%s" % destination,
    *[str(source) for source in sources]
  ])

@cli.log.LoggingApp
def generate_nuclear_masks_cli(app):
  for source in app.params.sources:
    try:
      GenerateNuclearMasksJob(
        source,
        app.params.destination,
      ).run()
    except Exception as exception:
      traceback.print_exc()

generate_nuclear_masks_cli.add_param("sources", nargs="*")
generate_nuclear_masks_cli.add_param("--destination", required=True)

if __name__ == "__main__":
   generate_nuclear_masks_cli.run()
