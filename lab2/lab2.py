#!/usr/bin/env python3

# NO IMPORTS! (except in the last part of the lab; see the lab writeup for details)
#import math
from PIL import Image

# COPIED FROM PREVIOUS LAB
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

def empty_image(image, val=0):
    """
	Helper function. Alias of black_image function, for convenience.
    """
    return black_image(image, val=0)

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
    Generator. Yields an (iterable) iterator with all (x, y) tuple coordinates on the image.
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




















# LAB 2 STARTS HERE!

# VARIOUS FILTERS

def split_colors(image):
    """
    Helper function. Given an image, splits into 3 images (one per RGB color). 
    Returns tuple of such images.
    """
    return tuple({'height':image['height'],
                  'width':image['width'],
                  'pixels':[p[i] for p in image['pixels']]} 
                   for i in range(3))

def recombine_colors(r,g,b):
    """
    Helper function. Given 3 images (one for each RGB color) of the same 
    size (check size), combines the three images and returns full image.
    """
    assert len({img['width'] for img in (r,g,b)})==1
    assert len({img['height'] for img in (r,g,b)})==1

    return {'width':r['width'],
            'height':r['height'],
            'pixels':list(zip(r['pixels'], g['pixels'], b['pixels']))}

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def _inner(image):
        filtered=tuple(filt(img) for img in split_colors(image))
        return recombine_colors(*filtered)
    return _inner

def make_blur_filter(n):
    return lambda image: blurred(image,n) 

def make_sharpen_filter(n):
    return lambda image: sharpened(image,n)


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def _inner(img):
        for filt in filters:
            img=filt(img)
        return img
    return _inner

# SEAM CARVING

# Main Seam Carving Implementation

def greyscale_image_from_color_image(image):
    """
    Returns a greyscale version of the given color image
    """
    return {
        'height': image['height'],
        'width': image['width'],
        'pixels': [round(.299*r + .587*g + .114*b)
                        for r,g,b in image['pixels']],
    }

def compute_energy(grey):
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given an energy map, return a cumulative energy map, in which the value at
    each position is the total energy of the lowest-energy path from the top
    of the image to that pixel.
    """
    result = empty_image(energy)
    for c, r in get_coords(energy):
        if r == 0:
            # Top row is the same as energy
            set_pixel(result, c, 0, get_pixel(energy, c, 0))
        else:
            this_energy = get_pixel(energy, c, r)
            above_energy = min(get_pixel_expanded(result, c+i, r-1) for i in {-1, 0, 1})
            set_pixel(result, c, r, this_energy + above_energy)
    return result


def minimum_energy_seam(inp):
    """
    Given a cumulative energy map, returns a list of the indices into
    im['pixels'] associated with the seam that should be removed
    """
    bottom_r = inp['height']-1
    min_bottom_c = min(range(inp['width']), key=lambda col: get_pixel(inp, col, bottom_r))
    seam_vals = [(min_bottom_c, bottom_r)]

    # Go through the rows from second-from-bottom to top
    for r in range(bottom_r-1, -1, -1):
        last_col = seam_vals[-1][0]
        above_coords = [(last_col + dc, r) for dc in [-1, 0, 1]
                                           if 0 <= last_col + dc < inp['width']]
        # min returns the leftmost value in the case of ties. Therefore the order of
        # above_coords matters.
        min_energy_coord = min(above_coords, key=lambda coord: get_pixel_expanded(inp, *coord))
        seam_vals.append(min_energy_coord)

    return [index_1d(inp, *coord) for coord in seam_vals]


def image_without_seam(im, s):
    """
    Given an image and a list of indices, returns a new image with
    the associated pixels removed.
    """
    out = empty_image(im)
    out['pixels'] = im['pixels'][:]
    out['width'] -= 1
    for i in s:
        out['pixels'].pop(i)
    return out


def seam_carving_helper(image):
    """
    Returns a new image, which is the input image after having one seam
    removed.
    """
    energy = compute_energy(greyscale_image_from_color_image(image))
    cumulative_energy = cumulative_energy_map(energy)
    seam = minimum_energy_seam(cumulative_energy)
    return image_without_seam(image, seam)


def seam_carving(image, ncols):
    """
    Returns a new image, which is the input image after having `ncols`
    seams removed.
    """
    out = image
    for _ in range(ncols):
        out = seam_carving_helper(out)
    return out






# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES (given by lecturerer)

def load_greyscale_image(filename): #from lab 1
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

def save_greyscale_image(image, filename, mode='PNG'): #from lab 1
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

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


















if __name__ == '__main__':

    # Transforming filter from greyscale to color image; apply to sample image
    # with inverted filter.
    cat=load_color_image('test_images/cat.png')
    color_inverted=color_filter_from_greyscale_filter(inverted)
    save_color_image(color_inverted(cat),'outputs/cat_inverted.png')


    #applying blur filter 
    python=load_color_image('test_images/python.png')
    save_color_image(color_filter_from_greyscale_filter(make_blur_filter(9))(python),'outputs/python_blurred.png')

    #applying sharpen filter 
    sparrowchick=load_color_image('test_images/sparrowchick.png')
    save_color_image(color_filter_from_greyscale_filter(make_sharpen_filter(7))(sparrowchick),'outputs/sparrowchick_sharpened.png')

    #applying cascade of filters
    frog=load_color_image('test_images/frog.png')
    filter1 = color_filter_from_greyscale_filter(edges)
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    filt = filter_cascade([filter1, filter1, filter2, filter1])
    save_color_image(filt(frog),'outputs/frog_filter_cascade.png')



    


