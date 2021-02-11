from pathlib import Path

def source_path(source):
  path = Path(source)
  if not path.exists():
    raise Exception("source does not exist")
  return path

def destination_path(destination):
  path = Path(destination)
  if not path.exists():
    Path.mkdir(path, parents=True)
  elif not path.is_dir():
    raise Exception("destination already exists, but is not a directory")
  return path
