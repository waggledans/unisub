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


""" Module for parsing SubRip files (.srt extension)  """
import pinyin
import re
from srt_exceptions import SrtTimeFrameFormatException
from srt_exceptions import SrtTimeFrameShiftException
import logging
log = logging.getLogger(__name__)


class _CONST(object):
    """
    hacky way to define read-only class
    """
    # pattern to match time of the sub line
    # Example: 00:00:03,748 --> 00:00:06,901
    timePattern = r"\d+:\d+:[\d,\,]+"
    timeFramePattern = r"\s*(" + timePattern + ")\s+-->\s+(" + timePattern + ")"
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
        self.extractTimeFromTimeFrame()

    def extractTimeFromTimeFrame(self, timeFrame=None):
        if not self.timeFrame and timeFrame is not None:
            self.timeFrame = timeFrame
        if not self.timeFrame:
            self.startTime = 0
            self.endTime = 0
        else:
            match = re.match(CONST.timeFramePattern, self.timeFrame)
            # Example: 00:00:03,748 --> 00:00:06,901
            if (match):
                try:
                    self.startTimeSrt = match.group(1)
                    self.endTimeSrt = match.group(2)
                    self.updateSrtTime()
                    log.debug("matched %s in %s, parsed out %s and %s" %
                              (CONST.timeFramePattern, self.timeFrame,
                               self.startTimeSrt, self.endTimeSrt))
                    log.debug("updated startTime to %s or %f, "
                              "endTime to %s or %f" % (self.startTimeSrt,
                                                       self.startTime,
                                                       self.endTimeSrt,
                                                       self.endTime
                                                       )
                              )
                except SrtTimeFrameFormatException as e:
                    log.error("Bad srt format %s" % str(e))

    def updateSrtTime(self):
        self.startTime = _SrtEntry.convertFromSrtTime(self.startTimeSrt)
        self.endTime = _SrtEntry.convertFromSrtTime(self.endTimeSrt)

    @classmethod
    def convertFromSrtTime(cls, srtTime):
        """
        converts srt time given as 00:00:03,748
        into float number of seconds ie 3.748
        """
        times = srtTime.split(':')
        if(len(times) == 3):
            seconds = float(times[2].replace(',', '.'))
            secSrt = seconds + CONST.secondsInMinute*int(times[1]) + CONST.secondsInHour * int(times[0])
            log.debug("Converted %s into %f" % (srtTime, secSrt))
            return secSrt
        else:
            raise SrtTimeFrameFormatException(srtTime)

    @classmethod
    def convertToSrtTime(cls, seconds):
        """
        converts float number of seconds like 3.748
        into srt time given as 00:00:03,748
        """
        hoursSrt = int(seconds // CONST.secondsInHour)
        leftSeconds = seconds - hoursSrt*CONST.secondsInHour
        minSrt = int(leftSeconds // CONST.secondsInMinute)
        leftSeconds -= minSrt*CONST.secondsInMinute
        secSrt = "%06.3f" % leftSeconds
        secSrt = secSrt.replace('.', ',', 1)
        srtTime = "%(hours)02d:%(minutes)02d:%(seconds)s" % {'hours': hoursSrt,
                                                             'minutes': minSrt,
                                                             'seconds': secSrt
                                                             }
        log.debug("Converted %f into %s" % (seconds, srtTime))
        return srtTime

    def shiftFrame(self, seconds, incr=True, decr=False):
        """
        shift timeFrame by specified amount of seconds.
        Either incr or decr must be set to True (incr is default)
        Example: 00:00:03,748 --> 00:00:06,901 will become
        00:00:06,848 --> 00:00:10,001 if shifted by 3.1
        """
        if decr:
            incr = False
        if incr:
            log.debug("Shifting frame forward by %f seconds" % seconds)
            self.startTime += seconds
            self.endTime += seconds
        else:
            log.debug("Shifting frame backward by %f seconds" % seconds)
            if self.startTime < seconds:
                raise SrtTimeFrameShiftException("Cant shift earlier by more "
                                                 "than %d" % self.startTime)
            self.startTime -= seconds
            self.endTime -= seconds
        self.startTimeSrt = _SrtEntry.convertToSrtTime(self.startTime)
        self.endTimeSrt = _SrtEntry.convertToSrtTime(self.endTime)
        self._updateTimeFrame()

    def _updateTimeFrame(self, startTime=None, endTime=None):
        """updates srt entry timeFrame to new value"""
        if startTime is None:
            startTime = self.startTimeSrt
        if endTime is None:
            endTime = self.endTimeSrt
        self.timeFrame = self._buildTimeFrame(startTime, endTime)

    def _buildTimeFrame(self, startTime=None, endTime=None):
        """
        builds srt entry timeFrame to smth like
        00:00:03,748 --> 00:00:06,901
        """
        if startTime is None:
            startTime = self.startTimeSrt
        if endTime is None:
            endTime = self.endTimeSrt
        return startTime + " --> " + endTime

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

    def toString(self):
        return self.subNumber + self.timeFrame + self.subText


class SrtObject(object):
    srtDB = {}
    filename = ""

    def __init__(self, srtDB):
        #  init class members ######
        self.srtDB = srtDB
        self.filename = ""
        self.name = "unknown_file"

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
        srtDB.name = filename
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
                if(re.match(CONST.currentSubNumberPattern, line) and not
                   saveOn):
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
                        saveOn = False
                        # saveOn is false, move to the next sub
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
        log.debug("merging 2 srt files")
        subs_merged = {}
        for key1 in self.srtDB:
            if (subs2.srtDB[key1]):
                record1 = self.srtDB[key1]
                record2 = subs2.srtDB[key1]
                record = _SrtEntry(record1.subNumber, record1.timeFrame,
                                   record1.subText + record2.subText)
                subs_merged[key1] = record
            else:
                # TODO:: try to find matching sub  (closest in time maybe?)
                log.debug("key {} is not found in sub being merged: {!s}".
                          format(key1, record1))
        return SrtObject(subs_merged)

    def printSrt(self, filename):
        """
        Prints subtitles object in .srt format
        """
        log.debug("printing srt to {!r}".format(filename))
        srtfile = open(filename, "w")
        for key in sorted(self.srtDB):
            srtfile.write(self.srtDB[key].toString())
            srtfile.write("\n")
        srtfile.close()

    def srtHanziToPinyin(self):
        """
        Converts all hanzi to pinyin
        """
        log.debug("Converting hanzi to pinyin")
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
        log.debug("adding pinyin to hanzi")
        subs_merged = {}
        for key in self.srtDB:
            one_sub = self.srtDB[key]
            pin = pinyin.get(one_sub.subText)
            new_sub = _SrtEntry(one_sub.subNumber, one_sub.timeFrame,
                                one_sub.subText + pin)
            subs_merged[key] = new_sub
        return SrtObject(subs_merged)
