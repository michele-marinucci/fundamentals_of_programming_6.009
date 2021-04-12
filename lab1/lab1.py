"""IMAGE PROCESSING, FIRST PART - LAB 1"""
#!/usr/bin/env python3
from PIL import Image as Image
# NO ADDITIONAL IMPORTS USED!

##PART 1 - DEFINE SOME HELPER FUNCTIONS
def index_1d(image,x,y):
	"""
	Helper function. Converts image's 2d index into a 1d index
	"""
	w=image['width']
	return w*y+x

def black_image(image, val=0):
	"""
	Helper function. Creates a balck image of the same size as the input image
	"""
	return {'height': image['height'],
		    'width': image['width'],
			'pixels': [val for _ in image['pixels']]}

def get_pixel(image, x, y):
	"""
	Helper function. Returns color i.e. pixel value at position x,y in the image.
	"""
	return image['pixels'][index_1d(image,x,y)]		

def set_pixel(image, x, y, c):
	"""
	Helper function. Sets color i.e. pixel value at position x,y in the image.
	"""
	image['pixels'][index_1d(image,x,y)] = c
	
def get_coords(image):
	"""
    Helper function. Yields all (x, y) tuple coordinates on the image.
    """
	for y in range(image['height']):
		for x in range(image['width']):
			yield x,y
	
def apply_per_pixel(image, func):
    """
	Helper funtion. Given a certain function, applies that function to every pixel within an image.
    """
    result = black_image(image)
    for x,y in get_coords(image):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x,y, newcolor)
    return result

#def inverted(image):
#	"""
#	Inverts the image, making bright pixels dark and viceversa.
#	"""
#	return apply_per_pixel(image, lambda c: 255-c)



## PART 2 - DEFINE FILTERS AND MORE HELPER FUNCTIONS

def clip(k,hi,lo):
	"""
	Helper function. Makes sure numbers don't fall out of range; clips numbers that do.
	"""
	return  max(min(hi,k),lo)

def get_pixel_expanded(image, x, y):
	"""
	Helper function. Expanded version of get_pixel; returns color i.e. pixel value at 
	position x,y in the image. If outside of image, rather than padding with zeros, this
	function pads with closest border pixel within image. 
	"""
	return get_pixel(image,
				     clip(x,image['width']-1,0),
				     clip(y,image['height']-1,0))
	
def correlate(image, kernel):
	"""
    Helper function. Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Kernel is a 2-d array, i.e. list of lists, representing a square matrix.
	"""
	out=black_image(image)
	n=len(kernel)
	for x,y in get_coords(image):
		v=0 #pixel value
		for kx in range(n): #coord x of kernel
			for ky in range(n): #coord y of kernel
				px=x-n//2+kx
				py=y-n//2+ky
				v+=get_pixel_expanded(image,px,py)*kernel[kx][ky]
		set_pixel(out, x, y, v)
	return out

def round_and_clip_image(image):
	"""
    Helper function. Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
	"""
	image['pixels']=[clip(round(i),255,0) for i in image['pixels']]
	return image

# FILTERS

def inverted(image):
	"""
	Inverts the image, making bright pixels dark and viceversa.
	"""
	return apply_per_pixel(image, lambda c: 255-c)

def blur_kernel(n,scale=1):
	"""
	Creates a n x n blur kernel (which takes average of all elements when used),
	scaled by a factor (default scale of 1)
	"""
	val=1/(n**2)*scale
	return [[val]*n for _ in range(n)]

def blurred(image, n):
	"""
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
	"""
	return round_and_clip_image(correlate(image, blur_kernel(n)))

def sharpened(image,n):
	"""
	Makes the image sharper by applying the formula 2*image-blurred_image to
	each pixel.	Inputs include an image and size of blur_kernel n. 
	"""
	blurred_image=correlate(image, blur_kernel(n))
	out={'height':image['height'],
	     'width':image['width'],
		 'pixels':[2*i-j for i,j in zip(image['pixels'],blurred_image['pixels'])]}
	return round_and_clip_image(out)

def edges(image):
	kx=[[-1,0,1],[-2,0,2],[-1,0,1]]
	ky=[[-1,-2,-1],[0,0,0],[1,2,1]]
	ox=correlate(image,kx)
	oy=correlate(image,ky)
	out={'height':image['height'],
	     'width':image['width'],
		 'pixels':[round((i**2+j**2)**.5) for i,j in zip(ox['pixels'],oy['pixels'])]}
	return round_and_clip_image(out)

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES (given by lecturerer)

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}

def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

if __name__ == '__main__':
	# code in this block will only be run when you explicitly run your script
	
	#apply inverted
	bluegill=load_image('test_images/bluegill.png')
	save_image(inverted(bluegill),'outputs/bluegill_inverted.png')
	
	#apply correlate (in this instance, with a translation kernel)
	pigbird= load_image('test_images/pigbird.png')
	kernel_translation=[[0]*9 for _ in range(9)]; kernel_translation[0][2]=1
	save_image(round_and_clip_image(correlate(pigbird, kernel_translation)),'outputs/pigbird_translated.png')
	
	#apply blur (through correlate)
	cat= load_image('test_images/cat.png')
	save_image(round_and_clip_image(correlate(cat, blur_kernel(5))),'outputs/cat_blurred.png')
	
	#apply sharpened
	python= load_image('test_images/python.png')
	save_image(sharpened(python,11),'outputs/python_sharpened.png')
	
	#apply edge detection
	construct= load_image('test_images/construct.png')
	save_image(edges(construct),'outputs/construct_edge_detection.png')
	
	
	
	
	
	
	