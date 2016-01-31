# unisub

Unisub is used by Chinese learners that didn't learn enough characters to read subtitles
and yet they want to watch Chinese movies with Chinese subs.
It could also be used to combine two different subs files into one

## The method

1. Find a movie in Chinese
2. Find subtitles file in SubRip format in Chinese
3. Generate pinyin file that matches Chinese subtitles:
  `bin/merge.py -i <your-chinese-subfile> -o <pinyin-file>`
4. Optionally you can merge <chinese.srt> and <pinyin.srt>
  `bin/merge.py -i <your-chinese-subfile> -o <pinyin-file> -c`
5. Load new subtitles file and watch a movie with both Hanzi and Pinyin subs

See `bin/merge.py --help` for more information.
