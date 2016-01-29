#!/usr/bin/env python
import tempfile
import unittest
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
from unisub import unisub


class TestPinyin(unittest.TestCase):
    def setUp(self):
        super(self.__class__,self).setUp()
        import os
        #TODO:: figure out how to get the path to hanzi.srt
        self.in_file = os.getcwd() + "/tests/files/hanzi.srt"
        self.ref_file = os.getcwd() + "/tests/files/hanzi_pinyined.srt"

    def tearDown(self):
        super(self.__class__,self).tearDown()

    def testConvert(self):
        srtDBToModify = unisub.SrtObject.fromFilename(self.in_file)
        srtDBToAdd = srtDBToModify.srtHanziToPinyin()
        #srtDBRef = unisub.SrtObject.fromFilename(self.ref_file)
        test_file = tempfile.NamedTemporaryFile(delete=False)
        test_file_name = test_file.name
        try:
            srtDBToAdd.printSrt(test_file_name)
            ref = open(self.ref_file,"r")
            for line in ref: 
                print(line)
            test_file.close()
            ref.close()	
        finally:
        #     os.remove(test_file_name)
            print test_file_name

