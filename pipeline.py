import traceback
from datetime import datetime
from threading import Thread

import cli.log

from generate_all_cropped_cell_images import GenerateAllCroppedCellImagesJob
from generate_all_distance_transforms import GenerateAllDistanceTransformsJob
from generate_all_maximum_projections import GenerateAllMaximumProjectionsJob
from generate_all_nuclear_masks import GenerateAllNuclearMasksJob
from generate_all_nuclear_segmentations import \
    GenerateAllNuclearSegmentationsJob
from generate_all_spot_positions import GenerateAllSpotPositionsJob
from generate_all_spot_result_lines import GenerateAllSpotResultLinesJob
from generate_spot_results_file import GenerateSpotResultsFileJob
from models.paths import *


class PipelineJob:
  def __init__(self, source, destination):
    self.source = source
    self.destination = destination
  
  def run(self):
    GenerateAllMaximumProjectionsJob(self.source_path, self.maximium_projections_and_z_centers_path).run()
    GenerateAllNuclearSegmentationsJob(self.maximium_projections_and_z_centers_path, self.nuclear_segmentations_path, diameter=100).run()
    GenerateAllNuclearMasksJob(self.nuclear_segmentations_path, self.nuclear_masks_path).run()
    
    def generate_distance_transforms():
      GenerateAllDistanceTransformsJob(self.nuclear_masks_path, self.distance_transforms_path).run()
    generate_distance_transforms_thread = Thread(target=generate_distance_transforms)
    generate_distance_transforms_thread.start()

    def generate_all_cropped_cell_images():
      GenerateAllCroppedCellImagesJob(self.maximium_projections_and_z_centers_path, self.nuclear_masks_path, self.cropped_cell_images_path).run()
    generate_all_cropped_cell_images_thread = Thread(target=generate_all_cropped_cell_images)
    generate_all_cropped_cell_images_thread.start()

    generate_distance_transforms_thread.join()
    generate_all_cropped_cell_images_thread.join()

    GenerateAllSpotPositionsJob(self.cropped_cell_images_path, self.spot_positions_path).run()
    GenerateAllSpotResultLinesJob(
      self.spot_positions_path,
      self.cropped_cell_images_path,
      self.distance_transforms_path,
      self.nuclear_masks_path,
      self.spot_result_lines_path
    ).run()
    GenerateSpotResultsFileJob(self.spot_result_lines_path, self.destination_path).run()

  @property
  def source_path(self):
    if not hasattr(self, "_source_path"):
      self._source_path = source_path(self.source)
    return self._source_path
  
  @property
  def destination_path(self):
    if not hasattr(self, "_destination_path"):
      self._destination_path = destination_path(self.destination)
    return self._destination_path

  @property
  def maximium_projections_and_z_centers_path(self):
    return self.destination_path / "maximum_projections_and_z_centers"
  
  @property
  def nuclear_segmentations_path(self):
    return self.destination_path / "nuclear_segmentations"
  
  @property
  def nuclear_masks_path(self):
    return self.destination_path / "nuclear_masks"
  
  @property
  def distance_transforms_path(self):
    return self.destination_path / "distance_transforms"
  
  @property
  def cropped_cell_images_path(self):
    return self.destination_path / "cropped_cell_images"

  @property
  def spot_positions_path(self):
    return self.destination_path / "spot_positions"
  
  @property
  def spot_result_lines_path(self):
    return self.destination_path / "spot_result_lines"
  
@cli.log.LoggingApp
def generate_spot_results_file_cli(app):
  try:
    PipelineJob(
      app.params.source,
      app.params.destination
    ).run()
  except Exception as exception:
    traceback.print_exc()

generate_spot_results_file_cli.add_param("source")
generate_spot_results_file_cli.add_param("destination")

if __name__ == "__main__":
   generate_spot_results_file_cli.run()
