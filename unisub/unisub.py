# encoding: utf-8

# Copyright (c) 2015 Dan Slov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


""" Module for parsing SubRip test files (.srt extension)  """
import pinyin
import re
from srt_exceptions import SrtTimeFrameFormatException
import logging
log = logging.getLogger(__name__)


class _CONST(object):
    """
    hacky way to define read-only class
    """
    # pattern to match time of the sub line
    # Example: 00:00:03,748 --> 00:00:06,901
    timeFramePattern = "\t*(\d+:\d+:[\d,\,]+).*--\>.*(\d.*)"
    # pattern to match ordinal number of the subtitle
    currentSubNumberPattern = "^\d+$"
    subSeparator = "^\t*$"
    secondsInMinute = 60
    secondsInHour = 3600

    def __setattr__(self, *_):
        pass


CONST = _CONST()


class _SrtEntry(object):
    """
    SubRip format entry example:
        0
        00:00:03,748 --> 00:00:06,901
        Huānyíng dàjiā lái xuéxí zhōngjí hànyǔ yǔfǎ
    Where first line is number, second is timeframe and
    the third is text
    """
    subNumber = 0
    timeFrame = ""
    subText = ""
    startTime = 0
    endTime = 1

    def __init__(self, subNumber=0, timeFrame="", subText=""):
        self.subNumber = subNumber
        self.timeFrame = timeFrame
        self.subText = subText

    def __str__(self):
        return self.subNumber + ' ' + self.timeFrame + ' ' + self.subText

    def __repr__(self):
        return ("subNumber: " + self.subNumber +
                ', timeFrame: ' + self.timeFrame + ',subText: ' + self.subText)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def extractTimeFromTimeFrame(self):
        if not self.timeFrame:
            self.startTime = 0
            self.endTime = 0
        else:
            match = re.match(CONST.timeFramePattern, self.timeFrame)
            # Example: 00:00:03,748 --> 00:00:06,901
            if (match):
                try:
                    self.startTime = _SrtEntry._convertSrtFormatTime(match.group(1))
                    self.endTime = _SrtEntry._convertSrtFormatTime(match.group(2))
                except SrtTimeFrameFormatException as e:
                    log.error("Bad srt format %s" % str(e))

    @classmethod
    def convertSrtFormatTime(srtTime):
        times = srtTime.split(':')
        if(len(times) == 3):
            # lastKey = match.group(1)
            mils = float(times[2].replace(',', '.'))
            return (mils + CONST.secondsInMinute*int(times[1]) +
                    CONST.secondsInHour * int(times[0]))
        else:
            raise SrtTimeFrameFormatException(srtTime)

    def toString(self):
        return self.subNumber + self.timeFrame + self.subText


class SrtObject(object):
    srtDB = {}
    filename = ""

    def __init__(self, srtDB):
        #  init class members ######
        self.srtDB = srtDB
        self.filename = ""

    def __str__(self):
        return str(self.srtDB)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.srtDB == other.srtDB
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def fromFilename(cls, filename):
        log.debug("parsing %s", filename)
        srtDB = cls({})
        srtDB.buildSrtDB(filename)
        return srtDB

    def buildSrtDB(self, filename=""):
        """ buildSrtDB takes .srt file name as an argument.
            Timeframe of each entry is used as a dictionary key
            The value of the dictionary is the object containing
            (number, time, text) of subtitle entry
        """
        if not filename:
            filename = self.filename
        srtfile = open(filename, "r")
        saveOn = False
        # saveOn is True when a line containing time to show subs is matched
        # saveOn is False when empty line is matched
        lastKey = "NONEMATCHED"
        subNumber = 0
        for line in srtfile:
            try:
                if(re.match(CONST.currentSubNumberPattern, line) and not saveOn):
                    # means we start a new sub
                    subNumber = line
                    continue
                match = re.match(CONST.timeFramePattern, line)
                # Example: 00:00:03,748 --> 00:00:06,901
                if (match):
                    srtEntry = _SrtEntry(subNumber, line)
                    startTimes = match.group(1).split(':')
                    if(len(startTimes) == 3):
                        saveOn = True
                        lastKey = match.group(1)
                        self.srtDB[lastKey] = srtEntry
                    else:
                        ermsg = "{} in {!r}".format(match.group(1), line)
                        raise SrtTimeFrameFormatException(ermsg)
                else:
                    if (re.match(CONST.subSeparator, line)):
                        saveOn = False    # saveOn is false, move to the next sub
                    if (saveOn):
                        # assuming multiline sub
                        log.debug("Text spans mutlitple lines: {!r}".format(line))
                        self.srtDB[lastKey].subText = self.srtDB[lastKey].subText + line
            except SrtTimeFrameFormatException as e:
                log.error("Bad srt format %s" % str(e))
        srtfile.close()

    def mergeSrtDB(self, subs2):
        """
        Merges two sub objects
        mergeSrtDB assumes that both dictionaries
        contain exactly the same set of keys
        """
        subs_merged = {}
        for key1 in self.srtDB:
            if (subs2.srtDB[key1]):
                record1 = self.srtDB[key1]
                record2 = subs2.srtDB[key1]
                record = _SrtEntry(record1.subNumber, record1.timeFrame,
                                   record1.subText + record2.subText)
                subs_merged[key1] = record
            else:
                log.debug("key {} is not found in sub being merged: {!s}".
                          format(key1, record1))
        return SrtObject(subs_merged)

    def printSrt(self, filename):
        """
        Prints subtitles object in .srt format
        """
        srtfile = open(filename, "w")
        for key in sorted(self.srtDB):
            srtfile.write(self.srtDB[key].toString())
            srtfile.write("\n")
        srtfile.close()

    def srtHanziToPinyin(self):
        """
        Converts all hanzi to pinyin
        """
        subs_pinyin = {}
        for key in self.srtDB:
            one_sub = self.srtDB[key]
            pin = pinyin.get(one_sub.subText)
            new_sub = _SrtEntry(one_sub.subNumber, one_sub.timeFrame, pin)
            subs_pinyin[key] = new_sub
        return SrtObject(subs_pinyin)

    def addPinyinToHanziSrt(self):
        """
        Appends pinyin to hanzi text
        """
        subs_merged = {}
        for key in self.srtDB:
            one_sub = self.srtDB[key]
            pin = pinyin.get(one_sub.subText)
            new_sub = _SrtEntry(one_sub.subNumber, one_sub.timeFrame,
                                one_sub.subText + pin)
            subs_merged[key] = new_sub
        return SrtObject(subs_merged)
