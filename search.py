# -*- coding: utf8 -*- 
import json
import sys
from collections import defaultdict
import argparse
import time

class ColorfulLog:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print_item(title, url, date):
        print ColorfulLog.OKGREEN + title + ColorfulLog.ENDC
        print ColorfulLog.WARNING + u'時間: ' + date + ColorfulLog.ENDC
        print ColorfulLog.UNDERLINE + url + ColorfulLog.ENDC

def commandline_arg(bytestring):
    unicode_string = bytestring.decode(sys.getfilesystemencoding())
    return unicode_string

def main():
    parser = argparse.ArgumentParser(description='Search article from craled data')
    parser.add_argument('-b', '--board', type=str,
        help='search article from ptt board')
    parser.add_argument('-k', '--keyword', type=commandline_arg, nargs='*',
        help='search article according to keywords')
    args = parser.parse_args()
    path = args.board
    keyword = [k for k in args.keyword]
    words = defaultdict(int)
    titles = []
    urls = []
    dates = []

    with open(path) as f:
        posts = json.load(f)

    start = time.time()

    for post in posts:
        content = post['content']
        title = post['title']
        for k in keyword:
            if title.find(k) != -1 and not post['url'] in urls:
                urls.append(post['url'])
                titles.append(post['title'])
                dates.append(post['date'])
        for l in content.split('\n'):
            if l:
                for k in keyword:
                    if l.find(k) != -1 and not post['url'] in urls:
                        urls.append(post['url'])
                        titles.append(post['title'])
                        dates.append(post['date'])

    for title, url, date in sorted(zip(titles, urls, dates), key=lambda x: x[2]):
        ColorfulLog.print_item(title, url, date)

    end = time.time()
    elapsed = end - start
    print "搜尋時間: ", "%.2f" % elapsed, "秒, 總共", len(titles), "筆資料"

if __name__ == '__main__':
    main()
