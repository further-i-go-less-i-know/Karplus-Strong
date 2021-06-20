"""
ks-real3.py
Uses the Karplus Strong algorithm to generate musical notes 
in a pentatonic scale.
Author: Mahesh Venkitachalam + Further

Further, yours truly, added "TwoNotesKS" function, the "readMusic" function, the'double' and 'delay' command line options, 
and a pyplot.pause().
 
2021

The original unaltered file from Mahesh can be found here: 
https://github.com/electronut/pp/blob/master/karplus/ks.py
"""

import sys, os
import time, random 
import wave, argparse, pygame 
import numpy as np
from collections import deque
from matplotlib import pyplot as plt

# show plot of algorithm in action?
gShowPlot = False

# notes of a Pentatonic Minor scale
# piano C4-E(b)-F-G-B(b)-C5
pmNotes = {'C4': 262, 'Eb': 311, 'F': 349, 'G':391, 'Bb':466}

def livePiano():
    """ASDFG keys on the keyboard play notes in real time. This makes your computer a primitive synth kind of. :D
       If the end-user clicks off the shell or even moves the shell the pygame.events are no longer registered.
    """
    notes = NotePlayer()
    pygame.init()
    import time
    go = True
    start_time = time.time()
    print(f"LivePiano start time: {time.asctime()}")
    print("Press a,s,d,f,g to play the 'piano' :) Also, do not move the shell or key input will be lost.")
    while go:
        if time.time() > (start_time + 10): #print every minute the program is still running
            print(f"Program still running {time.asctime()} ")
            start_time = time.time()
            
            
        for event in pygame.event.get():
            #print(f"[+] Got this event: {event}")
            #print(f"[+] type(event): {type(event)}")
            #print(f"[+] Event type is: {event.type}")
            name = pygame.event.event_name(event.type)
            #print(f"[+] Event name is: {name}")
            #print(f"[+] Event dict is: {event.dict}")
            d = event.dict
            if name == "KeyUp":
                try:
                    if 'unicode' in d.keys():
                        if d['unicode'] == 'a':
                           
                           notes.add("C4.wav")
                           notes.play("C4.wav")
                           #time.sleep(0.2)
                           
                        if d['unicode'] == 's':
                           notes.add("Eb.wav")
                           notes.play("Eb.wav")
                           #time.sleep(0.2)
                           
                        if d['unicode'] == 'd':
                           
                           notes.add("F.wav")
                           notes.play("F.wav")
                           #time.sleep(0.2)
                           
                        if d['unicode'] == 'f':
                           
                           notes.add("G.wav")
                           notes.play("G.wav")
                           #time.sleep(0.2)
                           
                        if d['unicode'] == 'g':
                           notes.add("Bb.wav")
                           notes.play("Bb.wav")
                           #time.sleep(0.2)
                           
                except Exception as e:
                        print("Exception ", e)
            
            
def readMusic(file):
    """Read music from a file. The text file should have a format like this: C4 1. 
       Which means play C4th octave then rest 1 second. 
    """
    with open(file) as music:
        lines = music.readlines()
        
    print(f"[+] Got these lines: {lines}")
    print("This is in the lines, item by item...")
    print("*" * 50)
    player = NotePlayer()
    for line in lines:
        print(line)# prints entire line
        items = line.split(" ")
        for item in items:
            item = item.replace('\n', '')
            if item.isdigit():
                print(f"{item} is a rest")
                time.sleep(int(item))
            else:
                print(f"{repr(item)} is a note")
                if os.path.exists(item + ".wav"):
                    if item + ".wav" in player.getNotes():
                        print(f" {item} already in notes dict")
                        player.play(item + '.wav')
                        
                    else:
                        player.add(item + '.wav')
                        player.play(item + '.wav')
                else:
                    #look up note
                    if item in pmNotes:
                        frequency = pmNotes[item]
                        data = generateNote(frequency)
                        writeWAVE(item + '.wav', data)
                        player.add(item + '.wav')
                        player.play(item + '.wav')
                    else:
                        print(f"[!] The note, {item}, found in {file} is not in the dictionary so I can't play it.") 
    print("*" * 50)

def TwoNotesKS(f1=349, f2=466, delay=False):
    """This method will replicate the sound of 2 strings of different frequencies.
        If delay is True then there will be a time delay between the first and second string
        plucks. f1 is the variable for frequency 1 in Hertz (hz). f2 is the variable for frequency 2
        in Hertz (hz). 
    """
    nSamples = 44100
    sampleRate = 44100
    N1 = int(sampleRate/f1)
    N2 = int(sampleRate/f2)
    # initialize ring buffer
    buf1 = deque([random.random() - 0.5 for i in range(N1)])
    buf2 = deque([random.random() - 0.5 for i in range(N2)])
    
    # init sample buffer
    samples1 = np.array([0]*nSamples, 'float32')
    samples2 = np.array([0]*nSamples, 'float32')
    for i in range(nSamples):
        samples1[i] = buf1[0]
        samples2[i] = buf2[0]
        
        avg1 = 0.995*0.5*(buf1[0] + buf1[1])
        buf1.append(avg1)
        buf1.popleft()

        avg2 = 0.995 * 0.5 * (buf2[0] + buf2[1])
        buf2.append(avg2)
        buf2.popleft()
                        
    if not delay:
        all_samples = samples1 + samples2
        # samples to 16-bit to string
        # max value is 32767 for 16-bit
        all_samples = np.array(all_samples * 32767, 'int16')
        return all_samples.tostring()
    if delay:
        sample1 = np.array(samples1 * 32767, 'int16')
        writeWAVE('sample1.wav', sample1)
        sample2 = np.array(samples2 * 32767, 'int16')
        writeWAVE('sample2.wav', sample2)
        note = NotePlayer()
        note.add('sample1.wav')
        note.add('sample2.wav')
        note.play('sample1.wav')
        time.sleep(1)
        note.play('sample2.wav')
        time.sleep(1)
   
# write out WAVE file
def writeWAVE(fname, data):
    # open file 
    file = wave.open(fname, 'wb')
    # WAV file parameters 
    nChannels = 1
    sampleWidth = 2
    frameRate = 44100
    nFrames = 44100
    # set parameters
    file.setparams((nChannels, sampleWidth, frameRate, nFrames,
                    'NONE', 'noncompressed'))
    file.writeframes(data)
    file.close()

# generate note of given frequency
def generateNote(freq):
    nSamples = 44100
    sampleRate = 44100
    N = int(sampleRate/freq)
    # initialize ring buffer
    buf = deque([random.random() - 0.5 for i in range(N)])
    # plot of flag set 
    if gShowPlot:
        axline, = plt.plot(buf)
    # init sample buffer
    samples = np.array([0]*nSamples, 'float32')
    for i in range(nSamples):
        samples[i] = buf[0]
        avg = 0.995*0.5*(buf[0] + buf[1])
        buf.append(avg)
        buf.popleft()  
        # plot of flag set 
        if gShowPlot:
            if i % 1000 == 0:
                axline.set_ydata(buf)
                plt.draw()
                plt.pause(.001)
            if i == (len(range(nSamples)) - 1):
                print("[+] Saving pyplot figure.")
                plt.savefig('notes')
            
                
      
    # samples to 16-bit to string
    # max value is 32767 for 16-bit
    samples = np.array(samples * 32767, 'int16')
    return samples.tostring()

# play a wav file
class NotePlayer:
    # constr
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        # dictionary of notes
        self.notes = {}
    # add a note
    def getNotes(self):
        return self.notes
    
    def add(self, fileName):
        self.notes[fileName] = pygame.mixer.Sound(fileName)
    # play a note
    def play(self, fileName):
        try:
            self.notes[fileName].play()
        except:
            print(fileName + ' not found!')
    def playRandom(self):
        """play a random note"""
        index = random.randint(0, len(self.notes)-1)
        note = list(self.notes.values())[index]
        note.play()

# main() function
def main():
    # declare global var
    global gShowPlot

    parser = argparse.ArgumentParser(description="Generating sounds with Karplus String Algorithm.")
    # add arguments
    parser.add_argument('--display', action='store_true', required=False)
    parser.add_argument('--play', action='store_true', required=False)
    parser.add_argument('--piano', action='store_true', required=False)
    parser.add_argument('--double', action='store_true', required=False)
    parser.add_argument('--delay', action='store_true', required=False)
    parser.add_argument('--read', action='store', required=False)
    parser.add_argument('--live', action='store_true', required=False)
    args = parser.parse_args()

    if args.read:
        readMusic(args.read)
        exit()

    # show plot if flag set
    if args.display:
        gShowPlot = True
        plt.ion()

    # create note player
    nplayer = NotePlayer()

    print('creating notes...')
    for name, freq in list(pmNotes.items()):
        fileName = name + '.wav' 
        if not os.path.exists(fileName) or args.display:
            data = generateNote(freq) 
            print('creating ' + fileName + '...')
            writeWAVE(fileName, data) 
        else:
            print('fileName already created. skipping...')
        
        # add note to player
        nplayer.add(name + '.wav')
        
        # play note if display flag set
        if args.display:
            nplayer.play(name + '.wav')
            time.sleep(0.5)
    
    # play a random tune
    if args.play:
        while True:
            try: 
                nplayer.playRandom()
                # rest - 1 to 8 beats
                rest = np.random.choice([1, 2, 4, 8], 1, 
                                        p=[0.8, 0.1, 0.05, 0.05])
                print(f"[+] 'rest' is type = {type(rest)}")
                print(f"[+] 'rest' = {rest}")
                time.sleep(0.25*rest[0])
            except KeyboardInterrupt:
                exit()

    # random piano mode
    if args.piano:
        while True:
            for event in pygame.event.get():
                if (event.type == pygame.KEYUP):
                    print("key pressed")
                    nplayer.playRandom()
                    time.sleep(0.5)

    #play 2 notes together
    if args.double and args.delay:
            print(f"[+] Double Delay Mode Engaged.")
            TwoNotesKS(delay=True)
            exit()
    if args.double:
        print("[*] Double mode engaged.")
        double_file = 'double.wav' 
        if not os.path.exists(double_file):
            double_data = TwoNotesKS() 
            print('creating ' + double_file + '...')
            writeWAVE(double_file, double_data) 
        else:
            print(f'{double_file} already created. skipping...')

        print("Playing double.wav...")
        nplayer.add(double_file)
        nplayer.play(double_file)
        time.sleep(2)
        print("[*] Double mode complete.")
        
    if args.read:
        print("[+] Read mode enagaged.")
        readMusic(file=args.read)
    
    if args.live:
        print("[+] Live piano mode engaged.")
        livePiano()
        
  
# call main
if __name__ == '__main__':
    main()
