# encoding: utf-8
import unittest
from unisub import unisub
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


class TestPinyin(unittest.TestCase):
    def testConvertHanzi(self):
        key = "00:00:03,748 --> 00:00:06,901"
        new_sub = unisub._SrtEntry(subNumber='0', timeFrame=key, subText="你好")
        srtDB = {key: new_sub}
        srt = unisub.SrtObject(srtDB)
        srtConverted = srt.srtHanziToPinyin()
        self.assertEqual('nǐhǎo', srtConverted.srtDB.get(key).subText)

    def testSrtHanziAndPinyinFileGenerate(self):
        pass
