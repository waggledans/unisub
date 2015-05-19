#!/usr/bin/env python
# reads and parses srt 

# imports section
# first add the directory to the search path
import os
import sys
import pinyin
import pprint
bindir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(bindir)
import re
# End of imports
class ParsedSrtFile(object):
    subs = {}
    filename = ""
    def __init__(self, **subs):
        #  init class members ######
        self.subs = subs
        self.filename = ""

    @classmethod
    def fromFilename(cls, filename):
        srtDB = cls()
        srtDB.srtToHash(filename)
        return srtDB

    def srtToHash(self,filename = ""):
        if not filename:
            filename = self.filename
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
##### temp variables ######
        saveOn = False  # saveOn is True when a line containing time to show subs is matched
        # saveOn is False when empty line is matched
        lastKey = "NONE"
        subNumber = 0
#####  variables ######
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
                    self.subs[lastKey] = (subNumber, line, "") 
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
                    record = self.subs[lastKey]
                    record = (record[0], record[1], record[2].join(line))
                    self.subs[lastKey] = record
        srtfile.close()
# mergeSameSrt appends subs2 to subs11
    def mergeSameSrt(self, subs2):
        """ 
        mergeSameSrt assumes that both dictionaries contain exactly the same set of keys
        """
        subs_merged = {}
        for key1 in self.subs:
            #subs[key1] = subs1[key1]
            if (subs2.subs[key1]):
                record1 = self.subs[key1]
                record2 = subs2.subs[key1]
                sub2 = record2[2]
                record = (record1[0], record1[1], record1[2] + sub2)
                subs_merged[key1] = record
        return ParsedSrtFile(**subs_merged)        

    def printSrt(self, filename):
        srtfile = open(filename,"w")
        for key in sorted(self.subs):
            for el in self.subs[key]:
                srtfile.write(el)
            srtfile.write("\n")
        srtfile.close()

    def addPinyinToEnglishSrt(subs):
        """ 
        addPinyinToEnglishSrt takes dictionary and returns new dictionary 
        containing hanzi and pinyin
        """
        subs_merged = {}
        for key1 in subs.subs:
            record1 = subs.subs[key1]
            pin = pinyin.get(record1[2])
            record = (record1[0], record1[1], record1[2] + pin)
            subs_merged[key1] = record
        return ParsedSrtFile(subs_merged)
class Date(object):
    day = 0
    month = 0
    year = 0

    def __init__(self, day=0, month=0, year=0):
        self.day = day
        self.month = month
        self.year = year
    @classmethod
    def from_string(cls, date_as_string):
        day, month, year = map(int, date_as_string.split('-'))
        date1 = cls(day, month, year)
        return date1
