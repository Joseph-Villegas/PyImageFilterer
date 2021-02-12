from PIL import Image

def invert(image):
	filtered_image = image.copy()
	# filtered_image.putdata(list(tuple(map(lambda pixel: (255 - pixel[0], 255 - pixel[1], 255 - pixel[2]), image.getdata()))))
	filtered_image.putdata([(255 - pixel[0], 255 - pixel[1], 255 - pixel[2]) for pixel in image.getdata()])
	return filtered_image

def grayscale(image):     
	return image.convert("L")

def swap_channels(image):
	filtered_image = image.copy()
	filtered_image.putdata([(pixel[2], pixel[0], pixel[1]) for pixel in image.getdata()])
	return filtered_image

def mask(image):
	filtered_image = image.copy()
	filtered_image.putdata([(0,)*3 if sum(pixel) / 3.0 < 128 else (255,)*3 for pixel in image.getdata()])
	return filtered_image