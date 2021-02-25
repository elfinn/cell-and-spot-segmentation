import json

class GenerateSpotPositionsConfig:
  @classmethod
  def from_json_params(cls, json_params):
    return cls(
      channel=json_params["channel"],
      local_contrast=json_params["local_contrast"],
      peak_radius=json_params["peak_radius"],
      global_threshold=json_params["global_threshold"]
    )

  def __init__(self, channel=None, local_contrast=None, peak_radius=None, global_threshold=None):
    super().__init__()
    self.channel = channel
    self.local_contrast = local_contrast
    self.peak_radius = peak_radius
    self.global_threshold = global_threshold

  def to_json_params(self):
    return {
      "channel": self.channel,
      "local_contrast": self.local_contrast,
      "peak_radius": self.peak_radius,
      "global_threshold": self.global_threshold
    }
