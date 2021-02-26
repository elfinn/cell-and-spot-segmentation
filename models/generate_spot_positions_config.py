import json

class GenerateSpotPositionsConfig:
  @classmethod
  def from_json_params(cls, json_params):
    return cls(
      channel=json_params["channel"],
      local_contrast_threshold=json_params["local_contrast_threshold"],
      peak_radius=json_params["peak_radius"],
      global_contrast_threshold=json_params["global_contrast_threshold"]
    )

  def __init__(self, channel=None, local_contrast_threshold=None, peak_radius=None, global_contrast_threshold=None):
    super().__init__()
    self.channel = channel
    self.local_contrast_threshold = local_contrast_threshold
    self.peak_radius = peak_radius
    self.global_contrast_threshold = global_contrast_threshold

  def to_json_params(self):
    return {
      "channel": self.channel,
      "local_contrast_threshold": self.local_contrast_threshold,
      "peak_radius": self.peak_radius,
      "global_contrast_threshold": self.global_contrast_threshold
    }
