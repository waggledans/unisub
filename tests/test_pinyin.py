#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from unisub import unisub


class TestPinyin(unittest.TestCase):
    def testConvertHanzi(self):
        key = "00:00:03,748 --> 00:00:06,901"
        new_sub = unisub._SrtEntry('0', key, "你好")
        srtDB = {key: new_sub}
        srt = unisub.SrtObject(srtDB)
        srtConverted = srt.srtHanziToPinyin()
        self.assertEqual(srtConverted.srtDB.get(key).subText, 'nǐhǎo')

    def testSrtHanziAndPinyinFileGenerate(self):
        pass
