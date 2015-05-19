#!/usr/bin/env python

# first add the directory to the search path
import getopt
import re
import os
import os.path
import pprint
import time
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
        hash1 = parse.ParsedSrtFile.fromFilename(file1)
        if len(sys.argv) > 3 and sys.argv[3] == 'pinyin':
            pinyin_subs = parse.addPinyinToEnglishSrt(hash1)
            pinyin_subs.printSrt(file2)
            sys.exit(0)
    else:
        sys.exit(3)
    if os.path.isfile(file2) and os.access(file2, os.R_OK):
        hash2 = parse.ParsedSrtFile.fromFilename(file2)
    else:
        sys.exit(4)
    subs = hash1.mergeSameSrt(hash2)    
    out_file = re.sub("\.srt$", "_merged.str", file1)
    subs.printSrt(out_file)

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
