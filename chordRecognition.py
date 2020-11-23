from math import log
from tkinter import filedialog
import contextlib
import wave
import numpy as np
import matplotlib.pyplot as plt
#In some versions it is needed to import array
#import array

# file name
filename = filedialog.askopenfilename()

# notes and frequencies
octaveN = ["C0","C#0","D0","D#0","E0","F0","F#0","G0","G#0","A0","A#0","B0","C1","C#1","D1","D#1","E1","F1","F#1","G1","G#1","A1","A#1","B1","C2","C#2","D2","D#2","E2","F2","F#2","G2","G2#","A2","A2#","B2","C3","C3#","D3","D3#","E3","F3","F3#","G3","G3#","A3","A3#","B3","C4","C4#","D4","D4#","E4","F4","F4#","G4","G4#","A4","A4#","B4","C5","C5#","D5","D5#","E5","F5","F5#","G5","G5#","A5","A5#","B5","C6","C6#","D6","D6#","E6","F6","F6#","G6","G6#","A6","A6#","B6","C7","C7#","D7","D7#","E7","F7","F7#","G7","G7#","A7","A7#","B7","C8","C8#","D8","D8#","E8","F8","F8#","G8","G8#","A8","A8#","B8","Beyond B8"]

octaveF = [16.35, 17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50, 29.14, 30.87, 32.70, 34.65, 36.71, 38.89, 41.20, 43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 61.74, 65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77, 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1975.53, 2093.00, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3729.31, 3951.07, 4186.01, 4434.92, 4698.64, 4978.03, 5274.04, 5587.65, 5919.91, 6271.93, 6644.88, 7040.00, 7458.62, 7902.13, 8000]

# Read a wave file and return the entire file as a standard array
def readWaveFile(infile,withParams=False,asNumpy=False):
    with contextlib.closing(wave.open(infile)) as f:
        params = f.getparams()
        frames = f.readframes(params[3])
        if(params[0] != 1):
            print("Warning in reading file: must be a mono file!")
        if(params[1] != 2):
            print("Warning in reading file: must be 16-bit sample type!")
        if(params[2] != 44100):
            print("Warning in reading file: must be 44100 sample rate!")
    if asNumpy:
        X = np.array(frames,dtype='int16')
    else:  
        X = array.array('h', frames)
    if withParams:
        return X,params
    else:
        return X
        
# return a list of triples of form  (f, A) for each frequency
# f detected by the transform
    
def spectrumFFT(X):
    S = []
    R = np.fft.rfft(X)
    WR = 44100/len(X)
    for i in range(len(R)):
        S.append( ( i*WR, 2.0 * np.absolute(R[i])/len(X) ) )
    return S
    
# return the closet note for the given frequency in term of (noteStr, noteFreq)

def findNote(F):
    refinedF = []
    
    for f in F:
        # find the key's index within an octave
        deviation = [abs(round(log(f / o, 2)) - log(f / o, 2)) for o in octaveF]
        i = deviation.index(min(deviation))
        
        # compute span relative to the 3rd octave
        span = round(log(f / octaveF[i], 2))
        
        # make sure this note is within the piano's range (A0 to C8)
        A0 = pow(2, 0-3) * octaveF[9]
        C8 = pow(2, 8-3) * octaveF[0]
        if A0 <= pow(2, span) * octaveF[i] <= C8:
            refinedF += [(octaveN[i] + str(3 + span), pow(2, span) * octaveF[i])]
    
    return refinedF

# filter the spectrum and get the frqeuencies loud enough to be heard
def spectrumFilter(S):
    F = []
    
    for (f, A) in S:
        if A > 350:
            F += [f]
    return F
    
def main():
    X1 = readWaveFile(filename)
    X = []
    
    # mu-law
    for i in range(len(X1)):
        y = log(1 + (255 * abs(X1[i]) / 32767), 2) / log(256, 2)
        if y != 0:
            X += [X1[i] * y]
        else:
            X += [0]
            
    xaxis = []    # time
    yaxis = []    # frequencies
    yname = []    # yticks (note names)
    ws = pow(2, 16)
    slide = pow(2, 14)
    index = 0
    
    while index < len(X):
        # slice off a window piece
        window = X[index : index + ws]
        
        # perform FFT on the window and filter the spectrum
        spectrum = spectrumFFT(window)
        F = spectrumFilter(spectrum)
        
        # find the closet notes for each frequency in terms of (noteName, noteFreq)
        freq = findNote(F)
        
        # add useful frequencies to the axises along with time
        for f in freq:
            xaxis += [(index + (ws / 2)) / 44100]
            yaxis += [f[1]]
            yname += [f[0]]
            
        index += slide

    # plot the graph   
    plt.scatter(xaxis, yaxis)
    plt.gca().set_xlim(0, len(X) / 44100)
    plt.gca().set_ylim(min(yaxis) / 2, max(yaxis) + 20)
    plt.yticks(yaxis, yname) 
    plt.grid(True)
    plt.show()

main()    