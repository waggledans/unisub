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


""" Module for modifying SubRip files (.srt extension)  """
import re
import unisub
from srt_exceptions import SrtTimeFrameFormatException
from srt_exceptions import SrtTimeFrameShiftException
import logging
log = logging.getLogger(__name__)


CONST = unisub._CONST()


class _ModSrtEntry(unisub._SrtEntry):
    """
    SubRip format entry example:
        0
        00:00:03,748 --> 00:00:06,901
        Huānyíng dàjiā lái xuéxí zhōngjí hànyǔ yǔfǎ
    Where first line is number, second is timeframe and
    third is text
    """
    startTime = 0
    endTime = 1

    def __init__(self, subNumber=0, timeFrame="", subText=""):
        kwargs = {'subNumber': subNumber,
                  'timeFrame': timeFrame,
                  'subText': subText
                  }
        super(self.__class__, self).__init__(**kwargs)
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
                    logging.error("Bad srt format %s" % str(e))

    def updateSrtTime(self):
        self.startTime = _ModSrtEntry.convertFromSrtTime(self.startTimeSrt)
        self.endTime = _ModSrtEntry.convertFromSrtTime(self.endTimeSrt)

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
        self.startTimeSrt = _ModSrtEntry.convertToSrtTime(self.startTime)
        self.endTimeSrt = _ModSrtEntry.convertToSrtTime(self.endTime)
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
