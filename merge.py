#!/usr/bin/env python

# first add the directory to the search path
import sys
import getopt
import re
import os
import os.path
from lib import parse

def main (argv):
    if len(sys.argv) < 3:
        print 'merge.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    file1 = sys.argv[1]
    file2 = sys.argv[2]

    if os.path.isfile(file1) and os.access(file1, os.R_OK):
        hash1 = parse.srtToHash(file1)
    else:
        sys.exit(3)
    if os.path.isfile(file2) and os.access(file2, os.R_OK):
        hash2 = parse.srtToHash(file2)
    else:
        sys.exit(4)
    subs = parse.mergeSameSrt(hash1, hash2)
    out_file = re.sub("\.srt$", "_merged.str", file1)
    parse.printSrt(out_file, subs)

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
