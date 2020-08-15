import os

class convert():

  @classmethod
  def resize(self, source_file, dest_file, display_height, display_width, fill=False):
    if (fill):
      command = 'convert {} -resize {}x{}^ -extent {}x{}  -background white -gravity center -alpha remove -rotate 90 {} '.format(
        source_file, display_height, display_width, display_height, display_width, dest_file
      )
      return os.system(command)
    else:
      command = "convert {} -resize {}x{} -extent {}x{} -background white -gravity center -alpha remove -rotate 90 {} ".format(
        source_file, display_height, display_width, display_height, display_width, dest_file
      )
      return os.system(command)
