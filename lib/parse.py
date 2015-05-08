#!/usr/bin/env python
# reads and parses srt 

# imports section
# first add the directory to the search path
import os
import sys
bindir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(bindir)
import re
# End of imports

#filename = sys.argv[1]
def srtToHash(filename):
    """ srtToHash takes .srt file name as an argument.
        The starting time of each entry is used as a dictionary key
        The value of the dictionary is the list (number, time, text)    
    """
    srtfile = open(filename,"r")
#lines = srtfile.readlines()
##### CONSTANTS ######
# pattern to match time of the sub line
    timePattern = "\t*(\d+:\d+:[\d,\,]+).*--.*\d"
    currentNumberPattern = "^\d+$"
    subSeparator = "^\t*$"
    secondsInMinute = 60
    secondsInHour = 3600
#
#####  variables ######
    subs = {}
##### temp variables ######
    saveOn = False  # saveOn is True when a line containing time to show subs is matched
    # saveOn is False when empty line is matched
    lastKey = "NONE"
    subNumber = 0
#####  variables ######
    subs = {}
    for line in srtfile: 
        #print(line)
        #line = line.rstrip()
        if(re.match(currentNumberPattern, line) and not saveOn): # means we start a new sub
            #subNumber = int(line)
            subNumber = line
        match = re.match(timePattern,line)
        if (match):
            times = match.group(1).split(':')
            if(len(times) == 3):
                saveOn = True
                lastKey = match.group(1)
                mils = float(times[2].replace(',','.'))
                # time variable will be used later when subtitles are not exact match
                time = mils + secondsInMinute*int(times[1]) + secondsInHour * int(times[0])
                subs[lastKey] = (subNumber, line, "") 
            else:
                # smth is wrong, TODO:: raise EXCEPTIONS
                # or maybe just do nothing
                continue
            #print(match.group(1))
        else:
            if (re.match(subSeparator, line)):
                saveOn = False    #saveOn is false, move on to the next sub
            if (saveOn):
                #assuming multiline sub
                record = subs[lastKey]
                record = (record[0], record[1], record[2].join(line))
                subs[lastKey] = record
    srtfile.close()
    return subs 
# mergeSameSrt appends subs2 to subs11
def mergeSameSrt(subs1, subs2):
    """ 
    mergeSameSrt assumes that both dictionaries contain exactly the same set of keys
    """
    subs = {}
    for key1 in subs1:
        #subs[key1] = subs1[key1]
        if (subs2[key1]):
            record1 = subs1[key1]
            record2 = subs2[key1]
            sub2 = record2[2]
            record = (record1[0], record1[1], record1[2] + sub2)
            subs[key1] = record
    return subs 
def printSrt(filename, subs):
    srtfile = open(filename,"w")
    for key in sorted(subs):
        for el in subs[key]:
            srtfile.write(el)
        srtfile.write("\n")
    srtfile.close()
