import os

class convert():
  @classmethod
  def resize(self, source_file, dest_file, display_height, display_width, fill=False):
    command_template =  'convert {source} -resize {height}x{width}\^ -extent {height}x{width} -background white -colorspace gray +dither -colors 16 -gravity center -alpha remove -rotate 90 {destination}'
    if (fill):
      command = command_template.replace(
        "{source}",
        source_file
      ).replace(
        "{height}",
        str(display_height)
      ).replace(
        "{width}",
        str(display_width)
      ).replace(
        "{destination}",
        dest_file
      )
      print("running", command)
      return os.system(command)
    else:
      command = "convert {} -resize {}x{} -extent {}x{} -background white -gravity center -alpha remove -rotate 90 {} ".format(
        source_file, display_height, display_width, display_height, display_width, dest_file
      )
      return os.system(command)
