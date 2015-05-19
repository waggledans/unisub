#!/usr/bin/env python

#Copyright (c) 2015 Dan Slov
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import getopt
import re
import os
import os.path
#import time
from lib import parse
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def main (argv):
    if len(sys.argv) < 3:
        print 'merge.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    if os.path.isfile(file1) and os.access(file1, os.R_OK):
        srtDBToModify = parse.SrtObject.fromFilename(file1)
        if len(sys.argv) > 3 and sys.argv[3] == 'pinyin':
            pinyin_subs = srtDBToModify.addPinyinToEnglishSrt()
            pinyin_subs.printSrt(file2)
            sys.exit(0)
    else:
        sys.exit(3)
    if os.path.isfile(file2) and os.access(file2, os.R_OK):
        srtDBToAdd = parse.SrtObject.fromFilename(file2)
    else:
        sys.exit(4)
    mergedSrtDB = srtDBToModify.mergeSrtDB(srtDBToAdd)    
    out_file = re.sub("\.srt$", "_merged.str", file1)
    mergedSrtDB.printSrt(out_file)

def longopts_example(argv):
   ifile = ''
   ofile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'merge.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         ifile = arg
      elif opt in ("-o", "--ofile"):
         ofile = arg
   print 'Input file is "', ifile
   print 'Output file is "', ofile

if __name__ == "__main__":
   main(sys.argv[1:])
