#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unisub import modisub, unisub


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
        # new_sub = modisub._ModSrtEntry('0', key, "hello")
        self.assertEqual(6.901, modisub._ModSrtEntry.convertFromSrtTime('00:00:06,901'))
        self.assertEqual('00:00:06,901', modisub._ModSrtEntry.convertToSrtTime(6.901))
