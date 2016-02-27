#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
import unittest
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
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

    def testConvertHanzi(self):
        key = "00:00:03,748 --> 00:00:06,901"
        new_sub = unisub._SrtEntry('0', key, "你好")
        srtDB = {key: new_sub}
        srt = unisub.SrtObject(srtDB)
        srtConverted = srt.srtHanziToPinyin()
        self.assertEqual(srtConverted.srtDB.get(key).subText, 'nǐhǎo')

    def testConvertSrtObject(self):
        self.assertEqual(self.srtDBToAdd, self.srtDBRef)

    def testSrtFileGenerate(self):
        test_file = tempfile.NamedTemporaryFile(delete=False)
        test_file_name = test_file.name
        try:
            self.srtDBToAdd.printSrt(test_file_name)
            with open(self.ref_file, 'r') as file_ref:
                with open(test_file_name, 'r') as file_test:
                    diffs = list(set(file_ref) - set(file_test))
            self.assertTrue(len(diffs) == 0)
        finally:
            os.remove(test_file_name)

    def testSrtHanziAndPinyinFileGenerate(self):
        pass

    def testSrtWrongFormat(self):
        pass
        #assertRaises()
