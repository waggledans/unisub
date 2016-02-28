#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unisub import unisub


class TestPinyin(unittest.TestCase):
    def setUp(self):
        super(self.__class__,self).setUp()
        import os
        files_dir = os.path.join(os.path.join(os.getcwd(), 'tests'), 'files')
        self.in_file = os.path.join(files_dir, 'hanzi.srt')
        self.ref_file = os.path.join(files_dir, 'hanzi_pinyined.srt')
        self.srtDBToModify = unisub.SrtObject.fromFilename(self.in_file)
        self.srtDBToAdd = self.srtDBToModify.srtHanziToPinyin()
        self.srtDBRef = unisub.SrtObject.fromFilename(self.ref_file)

    def testConvertTimeFormat(self):
        # key = "00:00:03,748 --> 00:00:06,901"
        # new_sub = unisub._SrtEntry('0', key, "hello")
        self.assertEqual(6.901, unisub._SrtEntry.convertFromSrtTime('00:00:06,901'))
        self.assertEqual('00:00:06,901', unisub._SrtEntry.convertToSrtTime(6.901))

    def testShiftFrame(self):
        key = "00:00:03,748 --> 00:00:06,901"
        new_sub = unisub._SrtEntry('0', key, "你好")
        oldStart = new_sub.startTime
        newStart = oldStart + 3.1
        new_sub.shiftFrame(3.1)
        self.assertEqual("%06.3f" % new_sub.startTime, "%06.3f" % newStart)
        new_sub.shiftFrame(3.1, decr=True)
        self.assertEqual("%06.3f" % new_sub.startTime, "%06.3f" % oldStart)
