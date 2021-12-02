#!/usr/bin/env python2
"""
Logpuzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Google's Python Class
http://code.google.com/edu/languages/google-python-class/

Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"

"""

import os
import re
import sys
import urllib
import argparse
from pip._vendor.progress.bar import ChargingBar as Bar


def read_urls(filename):
    """Returns a list of the puzzle urls from the given log file,
    extracting the hostname from the filename itself.
    Screens out duplicate urls and returns the urls sorted into
    increasing order."""
    with open(filename, 'r') as f:
        line = f.readline()
        pattern = "GET" + "(.+?)"+ "jpg"
        result = []

        while len(line) > 0:
            end_point = re.search(pattern, line)
            if end_point != None and end_point.group(0)[4:] not in result:
                if "no_picture" not in end_point.group(0)[4:]:
                    result.append(end_point.group(0)[4:])
            line = f.readline()
        return sorted(result, key = lambda x: x.split("/")[-1].split("-")[-1])


def download_images(img_urls, dest_dir, base_url="http://code.google.com"):
    """Given the urls already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory
    with an img tag to show each local image file.
    Creates the directory if necessary.
    """
    create_dir(dest_dir)
    img_tags = fetch_call(img_urls, dest_dir)
    create_html(dest_dir, img_tags)

def fetch_call(img_urls, dest_dir, base_url = "http://code.google.com"):
    img_tags = []
    max_urls = len(img_urls)
    bar = Bar('Processing', max=max_urls)

    for i, url in enumerate(img_urls):
        filename = "/img" + str(i) + ".jpg"
        filepath = dest_dir + filename
        if urllib.urlopen(base_url + url).getcode() == 200:
            urllib.urlretrieve(base_url + url, filepath)
            img_tags.append(filename)
        bar.next()
    bar.finish()
    return img_tags

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_html(path, images):
    img_tags = [ '<img src="' + "/" + path + image + '">' for image in images]
    html_file = ["<html>\n", "<body>\n"] + img_tags + ["</body>\n", "</html>"]

    with open(path + "/index.html", "w+") as f:
        for item in html_file:
            f.write(item)

def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--todir',  help='destination directory for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser

def main(args):
    """Parse args, scan for urls, get images from urls"""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)
    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
