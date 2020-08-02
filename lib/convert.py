import os

class convert():

  @classmethod
  def resize(self, source_file, dest_file, fill=False):
    if (fill):
      return os.system('convert {} -resize 528x880\! -background white -gravity center -alpha remove {}'.format(source_file, dest_file))
    else:
      return os.system("convert {} -resize 528x880 -extent 528x880 -background white -gravity center -alpha remove {}".format(source_file, dest_file))
