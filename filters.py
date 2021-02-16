from PIL import Image

# NOTE: the 'image' parameter is a PIL image object in all methods

""" Begin Helper Functions """

def bound(value):
	""" Enforces upper bound for color channels """
	return 255 if value > 255 else int(value)

def get_sepia_pixel(red, green, blue):
	""" Returns a sepia toned pixel """
	return (
		bound((0.759 * red) + (0.398 * green) + (0.194 * blue)),
		bound((0.676 * red) + (0.354 * green) + (0.173 * blue)),
		bound((0.524 * red) + (0.277 * green) + (0.136 * blue))
	)

""" End Helper Functions """

def invert(image):
	""" Applies invert filter to a PIL image object """
	filtered_image = image.copy()
	# filtered_image.putdata(list(tuple(map(lambda pixel: (255 - pixel[0], 255 - pixel[1], 255 - pixel[2]), image.getdata()))))
	filtered_image.putdata([(255 - pixel[0], 255 - pixel[1], 255 - pixel[2]) for pixel in image.getdata()])
	return filtered_image

def grayscale(image):
	""" Applies grayscale filter to a PIL image object """     
	return image.convert("L")

def swap_channels(image):
	""" Applies swap channels filter to a PIL image object """
	filtered_image = image.copy()
	filtered_image.putdata([(pixel[2], pixel[0], pixel[1]) for pixel in image.getdata()])
	return filtered_image

def mask(image):
	""" Applies mask filter to a PIL image object """
	filtered_image = image.copy()
	filtered_image.putdata([(0,)*3 if sum(pixel) / 3.0 < 128 else (255,)*3 for pixel in image.getdata()])
	return filtered_image

def sepia(image):
	""" Applies sepia filter to a PIL image object """
	filtered_image = image.copy()
	filtered_image.putdata([get_sepia_pixel(pixel[0], pixel[1], pixel[2]) for pixel in image.getdata()])
	return filtered_image

def contrast(image):
	""" Applies contrast filter to a PIL image object """
	filtered_image = image.copy()
	filtered_image.putdata([tuple(map(lambda value: bound(int(value / 2) if value < 128 else value * 2), pixel)) for pixel in image.getdata()])
	return filtered_image

def flip(image):
	""" Applies flip filter to a PIL image object """
	filtered_image = image.copy()
	width, height = filtered_image.size
	[filtered_image.putpixel((x, y), image.getpixel((x, height - y - 1))) for x in range(width) for y in range(height)]
	return filtered_image

def mirror(image):
	""" Applies mirror filter to a PIL image object """
	filtered_image = image.copy()
	width, height = filtered_image.size
	[filtered_image.putpixel((x,y), image.getpixel((width - x -1, y))) for x in range(int(width / 1)) for y in range(height)]
	return filtered_image
