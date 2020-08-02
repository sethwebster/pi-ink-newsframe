import os

class convert():

  @classmethod
  def resize(self, source_file, dest_file, fill = False):
    return os.system('convert {} -resize 528x880{} -background white -gravity center -alpha remove {}'.format(source_file, "\!" if fill else "", dest_file))
