#!/usr/bin/env python3
import argparse
import sys
import re

def search_file(regex, file, show_filename, show_line_number):
    found = False

    try:
        with open(file, mode='r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, start=1):
                if regex.search(line):
                    found = True
                    prefix_part = []
                    if show_filename:
                        prefix_part.append(file)
                    if show_line_number:
                        prefix_part.append(str(line_num))
                    
                    if prefix_part:
                        print(":".join(prefix_part) + ":" + line, end="")
                    else:
                        print(line, end="")

    except OSError as err:
        print(f"Error in opening the file {file}: {err}", file=sys.stderr)
    
    return found

def main():

    parser = argparse.ArgumentParser(
        description="Search pattern in file(s)"
    )
    parser.add_argument('pattern')
    parser.add_argument('files', nargs="+")
    
    parser.add_argument("-n", "--line_number",action="store_true",help="")
    parser.add_argument("-i","--ignore-case",action="store_true",help="")

    args = parser.parse_args()

    regex_flag = re.IGNORECASE if args.ignore_case else 0

    try:
        regex = re.compile(args.pattern, regex_flag)
    except re.error as exc:
        print(f"Failed parsing the arguments: {exc}", file=sys.stderr)
        return 2
    
    show_filename = len(args.files)>1
    show_line_number = args.line_number
    anymatch = False

    for file in args.files:
        matched = search_file(regex, file, show_filename, show_line_number)
        anymatch = anymatch or matched

    return 0 if anymatch else 1

if __name__=="__main__":
    raise SystemExit(main())