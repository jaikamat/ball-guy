class BMPReader(object):
    def __init__(self, filename):
        self._filename = filename
        self._read_img_data()

    def to_string(self):
        """
        Prints a string represenation of the image, returns nothing
        """
        print('Filename: ' + self._filename)
        print('Width: ' + str(self.width))
        print('Height: ' + str(self.height))
        print('Start position: ' + str(self._start_pos))
        print('End position: ' + str(self._end_pos))

    def _get_pixel(self, x, y, offset):
        return self._pixel_data[(x * 3) + (y * self.width * 3) + offset]

    def get_pixel_r(self, x, y):
        """
        Returns an integer with the red value at position (x,y)
        """
        return self._get_pixel(x, self.height-y-1, 2)
        
    def get_pixel_g(self, x, y):
        """
        Returns an integer with the green value at position (x,y)
        """
        return self._get_pixel(x, self.height-y-1, 1)
        
    def get_pixel_b(self, x, y):
        """
        Returns an integer with the blue value at position (x,y)
        """
        return self._get_pixel(x, self.height-y-1, 0)

    def get_pixels(self):
        """
        Returns a multi-dimensional array of the RGB values of each pixel in the
        image, arranged by rows and columns from the top-left.  Access any pixel
        by its location, eg:

        pixels = BMPReader(filename).get_pixels()
        top_left_px = pixels[0][0] # [255, 0, 0]
        bottom_right_px = pixels[8][8] # [0, 255, 255]
        """
        pixel_grid = []
        pixel_data = list(self._pixel_data) # So we're working on a copy

        for x in range(self.width):
            col = []
            for y in range(self.height):
                r = pixel_data.pop()
                g = pixel_data.pop()
                b = pixel_data.pop()
                col.append((r, g, b))
            col.reverse()
            pixel_grid.append(col)

        return pixel_grid

    def _read_img_data(self):
        with open(self._filename, 'rb') as f:
            
            # [0:2] BM header
            header = f.read(2) 
            assert header[0] == 66 and header[1] == 77, "Not a valid BMP file"
            
            # Discard [2:10]
            f.read(8) 
            
            # [10:14] start_pos
            self._start_pos = int.from_bytes(f.read(4), "little")
            
            # Discard [14:18]
            f.read(4) 
            
            # [18:22] width, [22:26] width
            self.width = int.from_bytes(f.read(4), "little") 
            self.height = int.from_bytes(f.read(4), "little")
            
            # Discard [26:28]
            f.read(2) 
            
            # [28:30] bits per pixel
            assert int.from_bytes(f.read(2), "little") == 24, \
                   "Only 24-bit colour depth is supported"
            
            # [30:34] compression
            assert int.from_bytes(f.read(4), "little") == 0, \
                   "Compression is not supported"
            
            # [34:38] end_pos
            self._end_pos = int.from_bytes(f.read(4), "little")

        # As per https://en.wikipedia.org/wiki/BMP_file_format for BI_RGB
        # images, length can be 0, so it can be inferred from the image size
        if self._end_pos == 0:
            self._end_pos = self.width * self.height * 3

        self._end_pos = self._start_pos + self._end_pos

        with open(self._filename, 'rb') as f:
            # Discard up to start_pos
            f.read(self._start_pos)

            # Read the RGB data from start to end
            self._pixel_data = f.read(self._end_pos)
