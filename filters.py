from PIL import Image

def invert(image):
	filtered_image = image.copy()
	# filtered_image.putdata(list(tuple(map(lambda pixel: (255 - pixel[0], 255 - pixel[1], 255 - pixel[2]), image.getdata()))))
	filtered_image.putdata([(255 - pixel[0], 255 - pixel[1], 255 - pixel[2]) for pixel in image.getdata()])
	return filtered_image