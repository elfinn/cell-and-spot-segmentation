import skimage

class NuclearMask:
  def __init__(self, mask, offset):
    self.mask = mask
    self.offset = offset

  @classmethod
  def build(cls, masks, regionprops):
    (min_row, min_col, max_row, max_col) = regionprops.bbox
    offset = (min_row, min_col)
    mask = masks[min_row:max_row, min_col:max_col] == regionprops.label
    return cls(mask, offset)
