# No Imports used!

def backwards(sound):
	"""
	Creates backwards version of a sound
	"""
	return {'rate':sound['rate'],
			'left':sound['left'][::-1],
			'right':sound['right'][::-1]}

def mix_sample_list(s1_list,s2_list,duration,p):
	"""
	Helper function for mix function: given the minimum duration of two sound samples
	(both right or both left) and given a mixing parameter p, sum the two samples weighted by p  
	"""
	return [i*p+j*(1-p) for i,j in zip(s1_list[:duration],s2_list[:duration])]

def mix(sound1, sound2, p):
	"""
	Mixes two sounds according to a mixing parameter p
	"""
	if sound1['rate']!=sound2['rate']: return None 
	duration=min(len(sound1['left']),len(sound2['left']))
	return {'rate':sound1['rate'],
			'left':mix_sample_list(sound1['left'],sound2['left'],duration,p),
			'right':mix_sample_list(sound1['right'],sound2['right'],duration,p)}

def echo_sample_list(sample_list, num_echos, delay_in_samples, scale):
	"""
	Helper function for echo function
	"""
	out=[0]*(len(sample_list)+num_echos*delay_in_samples)
	for i in range(num_echos+1):
		this_scale=scale**i
		offset=i*delay_in_samples
		for j in range(len(sample_list)):
			out[offset+j]+=sample_list[j]*this_scale	
	return out	

def echo(sound, num_echos, delay, scale):
	"""
	Creates an echo effect to a sound, where num_echos is the number of repetitions, delay is the
	delay in seconds, and scale is a factor representing the decrease in volume at each repetion
	"""
	
	delay_in_samples = round(delay * sound['rate'])
	return {'rate':sound['rate'],
			'left':echo_sample_list(sound['left'], num_echos, delay_in_samples, scale),
			'right':echo_sample_list(sound['right'], num_echos, delay_in_samples, scale)}

def pan(sound):
	"""
	Create a sound effect using two speakers; the sound from right speacker will increase as
	the sound from the left speaker descreases
	"""
	
	N=len(sound['left'])
	left,right=[],[]
	for i in range(N):
		right_scale=i/(N-1)   
		left_scale=1-right_scale
		right.append(sound['right'][i]*right_scale)
		left.append(sound['left'][i]*left_scale)
	return {'rate':sound['rate'],'left':left,'right':right}

def remove_vocals(sound):
	"""
	Removes vocals from a song, leaving only instruments
	"""
	   diff=[i-j for i,j in zip(sound['left'],sound['right'])]
	   return {'rate':sound['rate'],'left':diff,'right':diff}

# Below are two helper functions provided by lecturer for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run this script
	
	#apply backwards
	mystery = load_wav('sounds/mystery.wav')
	write_wav(backwards(mystery), 'mystery_backwards.wav')	
	
	#apply mix
	synth = load_wav('sounds/synth.wav')
	water = load_wav('sounds/water.wav')
	write_wav(mix(synth,water,0.2), 'synth_water_mix.wav')

	#apply echo
	chord = load_wav('sounds/chord.wav')
	write_wav(echo(chord,5,0.3,0.6),'chord_echo.wav')

	#apply pan
	car = load_wav('sounds/car.wav')
	write_wav(pan(car),'car_pan.wav')
	
	#apply remove_vocals
	coffee= load_wav('sounds/coffee.wav')
	write_wav(remove_vocals(coffee),'coffee_remove_vocals.wav')



