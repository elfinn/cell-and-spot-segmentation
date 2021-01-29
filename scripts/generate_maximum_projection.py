import cli.log

class GenerateMaximumProjectionJob:
  def __init__(self, source_image_prefix, destination):
    self.source_image_prefix = source_image_prefix
    self.destination = destination

  def start(self):
    # read all the images
    # maximially project them
    # compute the z-axis distance distribution
    # serialize it all out, probably via `numpy.save(Path(self.destination) / ("%_maximal_projection.npy" % self.source_image_prefix))`
    pass

def generate_maximum_projection_cli_str(source_image_prefix, destination):
  # TODO: not sure this file will be in the path in swarm. might need to configure the swarm env?
  return "pipenv run python %s %s %s" % (__file__, source_image_prefix, destination)

@cli.log.LoggingApp
def generate_maximum_projection_cli(app):
  generate_all_maximum_projections(app.params.source_image_prefix, app.params.destination)

generate_maximum_projection_cli.add_param("source_image_prefix")
generate_maximum_projection_cli.add_param("destination")

if __name__ == "__main__":
  generate_maximum_projection_cli.run()
