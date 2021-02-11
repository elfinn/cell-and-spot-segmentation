def distinct_labels(label_matrix):
  distinct_labels_set = set()
  for labels_row in label_matrix:
      for label in labels_row:
          distinct_labels_set.add(label)
  distinct_labels_set.remove(0)
  return [label for label in distinct_labels_set]

