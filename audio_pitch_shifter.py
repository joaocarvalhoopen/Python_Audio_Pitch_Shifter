###################################################################################################
# Project name: Python Audio Pitch Shifter
# Description: The program receives a input mono wav file at a sample rate of 44100 samples / sec
#              (can be other sample rate) and writes a new file , at the same sample rate with
#              the pitch shifted.
# Author: Joao Nuno Carvalho
# License: MIT Open Source License
# Note: This program was inspired by a great project with the AVR Tiny microcontroller:
#       Audio Pitch Shifter
#       http://www.technoblogy.com/show?1L02
#####################################################################################################

import numpy as np
import wave

def readWAVFilenameToArray(source_WAV_filename):
    # Read file from harddisc.
    wav_handler = wave.open(source_WAV_filename,'rb') # Read only.
    num_frames = wav_handler.getnframes()
    sampl_freq = wav_handler.getframerate()
    wav_frames = wav_handler.readframes(num_frames)

    # Loads the file into a NumPy contigous array.

    # Convert Int16 into float64 in the range of [-1, 1].
    # This means that the sound pressure values are mapped to integer values that can range from -2^15 to (2^15)-1.
    #  We can convert our sound array to floating point values ranging from -1 to 1 as follows.
    signal_temp = np.fromstring(wav_frames, 'Int16')
    signal_array = np.zeros( len(signal_temp), float)

    for i in range(0, len(signal_temp)):
        signal_array[i] = signal_temp[i] / (2.0**15)

    return signal_array, sampl_freq

def writeArrayToWAVFilename(signal_array, sampl_freq, destination_WAV_filename):
    # Converts the NumPy contigous array into frames to be writen into the file.
    # From range [-1, 1] to -/+ 2^15 , 16 bits signed
    signal_temp = np.zeros(len(signal_array), 'Int16')
    for i in range(0, len(signal_temp)):
        signal_temp[i] = int( signal_array[i] * (2.0**15) )

    # Convert float64 into Int16.
    # This means that the sound pressure values are mapped to integer values that can range from -2^15 to (2^15)-1.
    num_frames = signal_temp.tostring()

    # Wrtie file from harddisc.
    wav_handler = wave.open(destination_WAV_filename,'wb') # Write only.
    wav_handler.setnframes(len(signal_array))
    wav_handler.setframerate(sampl_freq)
    wav_handler.setnchannels(1)
    wav_handler.setsampwidth(2) # 2 bytes
    wav_handler.writeframes(num_frames)

def pitch_shift(input_WAV, factor, sample_rate):
    output_WAV = np.zeros(len(input_WAV))
    circular_buffer_length = 256
    circ_buf = np.zeros(circular_buffer_length)
    write_index = 0
    read_index = 0
    write_period = 1.0 / sample_rate
    read_period = write_period * factor
    for i in range(0, len(input_WAV)):
        # Write to the circular buffer.
        # To reduce the audible clicks when the two pointers cross we average the
        # existing value with the new value.
        circ_buf[write_index] = (circ_buf[write_index] + input_WAV[i]) / 2
        #circ_buf[write_index] = input_WAV[i]
        if write_index == circular_buffer_length - 1:
            write_index = 0
        else:
            write_index += 1

        # Calc the next read index on the circular buffer.
        t = i * write_period
        ri = t / read_period
        read_index = int(ri % circular_buffer_length)

        # Read from the circular buffer with different pitch.
        output_WAV[i] = circ_buf[read_index]

    return output_WAV


input_WAV_path  = "./Diana_track.wav"
output_WAV_path = "./Diana_track_shifted.wav"

factor = 1.25 # 1.25 # #0.75 # 0.5 # 1 is the same pitch, 2 halfes the pitch and 0.5 duplicates the pitch.

input_WAV, sample_rate = readWAVFilenameToArray(input_WAV_path)
# Pitch shifting.
output_WAV = pitch_shift(input_WAV, factor, sample_rate)
# output_WAV = input_WAV.copy()
writeArrayToWAVFilename(output_WAV, sample_rate, output_WAV_path)


