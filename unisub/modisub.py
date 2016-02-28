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
                    self.startTime = _ModSrtEntry.convertFromSrtTime(match.group(1))
                    self.endTime = _ModSrtEntry.convertFromSrtTime(match.group(2))
                except SrtTimeFrameFormatException as e:
                    logging.error("Bad srt format %s" % str(e))

    @classmethod
    def convertFromSrtTime(cls, srtTime):
        """
        converts srt time given as 00:00:03,748
        into float number of seconds ie 3.748
        """
        log.debug("Converting %s into seconds" % srtTime)
        times = srtTime.split(':')
        if(len(times) == 3):
            # lastKey = match.group(1)
            seconds = float(times[2].replace(',', '.'))
            return (seconds + CONST.secondsInMinute*int(times[1]) +
                    CONST.secondsInHour * int(times[0]))
        else:
            raise SrtTimeFrameFormatException(srtTime)

    @classmethod
    def convertToSrtTime(cls, seconds):
        """
        converts float number of seconds like 3.748
        into srt time given as 00:00:03,748
        """
        log.debug("Converting %f into srt format time" % seconds)
        hoursSrt = int(seconds // CONST.secondsInHour)
        leftSeconds = seconds - hoursSrt*CONST.secondsInHour
        minutesSrt = int(leftSeconds // CONST.secondsInMinute)
        secondsSrt = str(leftSeconds - minutesSrt*CONST.secondsInMinute).replace('.', ',', 1)
        if re.search(r'^\d,', secondsSrt):
            secondsSrt = '0' + secondsSrt
        srtTime = "%(hours)02d:%(minutes)02d:%(seconds)s" % {'hours': hoursSrt,
                                                             'minutes': minutesSrt,
                                                             'seconds': secondsSrt
                                                             }
        log.debug("Converted %f into %s" % (seconds, srtTime))
        return srtTime
