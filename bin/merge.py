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


import re
import os
import os.path
#import time
from unisub import unisub
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Converts hanzi srt into pinyin srt. Optionally could combine hanzi and pinyin into one.')
    help = "Original srt file."
    parser.add_argument('-i', '--in-srt', help=help, required = True)
    help = "Additional srt file"
    parser.add_argument('-e', '--extra-srt', help=help)
    help = "Output srt file"
    parser.add_argument('-o', '--out-srt', help=help)
    help = "Combining hanzi and pinyin into one srt file"
    parser.add_argument('-c', '--combine-srt', action='store_true', help=help)
    help = "Increase output verbosity"
    parser.add_argument("-v", "--verbosity", action="count", default=0, help=help)
    args = parser.parse_args()
    return args 
def main (argv):
    args = parse_args()
    if not args.out_srt:
	args.out_srt = re.sub( r".srt$", ".out.srt", args.in_srt)
    if os.path.isfile(args.in_srt) and os.access(args.in_srt, os.R_OK):
        srtDBToModify = unisub.SrtObject.fromFilename(args.in_srt)
	if not args.extra_srt:
            # srtDBToAdd = srtDBToModify.addPinyinToHanziSrt()
            srtDBToAdd = srtDBToModify.srtHanziToPinyin()
	    if not args.combine_srt:
		mergedSrtDB = srtDBToAdd
	elif os.path.isfile(args.extra_srt) and os.access(args.extra_srt, os.R_OK):
	    srtDBToAdd = unisub.SrtObject.fromFilename(args.extra_srt)
	    args.combine_srt = True
    else:
	print "Error - the file doesnt exist"
        sys.exit(1)
    if args.combine_srt:
	mergedSrtDB = srtDBToModify.mergeSrtDB(srtDBToAdd)
    mergedSrtDB.printSrt(args.out_srt)

if __name__ == "__main__":
   main(sys.argv[1:])
