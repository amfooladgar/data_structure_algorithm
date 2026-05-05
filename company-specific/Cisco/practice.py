import os
import argparse
import re
from pathlib import Path
import fnmatch
import sys

def search_paths(regex, filename, show_line_number, show_filenames, show_filenames_only):
    found = False

    try:
        with open(filename, mode="r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                if regex.search(line):
                    found = True
                    if show_filenames_only:
                        print(filename)
                        return True
                    
                    print(format_output(filename, line, show_line_number, line_number, show_filenames),
                        end="")
                    
    except OSError as osError:
        print(f"could not read file {filename} with error: {osError}", file=sys.stderr)
        return False

    return found

def build_parser():
    parser = argparse.ArgumentParser(
        description=""
    )
    parser.add_argument("pattern", help="")
    parser.add_argument("paths", nargs="+", help="")
    parser.add_argument("-n","--line-number", action="store_true", help="show matched line numbers")
    parser.add_argument("-i", "--ignore-case", action="store_true" ,help="")
    parser.add_argument("-l", "--match-files-only", action="store_true" ,help="")

    parser.add_argument("--include", help="example: --include=*.log")
    parser.add_argument("--exclude-dir", action="append", default=[])

    return parser

def should_include_file(file, pat):
    if pat is None:
        return True
    return fnmatch.fnmatch(file, pat)

def iter_files(paths, include_file, exclude_dir):
    
    for rawPath in paths:
        path = Path(rawPath)

        if path.is_file():
            if should_include_file(path, include_file):
                yield path
        
        elif path.is_dir():
            for root, dirnames, filenames in os.walk():

                dirnames[:] = [
                    dirname for dirname in dirnames
                    if dirname not in exclude_dir
                ]

                for filename in filenames:
                    if should_include_file(path, include_file):
                        yield (root) / filename
        else:
            print(f"no file is found!", file=sys.stderr)    
    

def format_output(filename, line, show_line_number, line_number, show_filenames):

    prefix_part = []
    if show_line_number:
        prefix_part.append(str(line_number))
    if show_filenames:
        prefix_part.append(str(filename))
    
    if prefix_part:
        return ":".join(prefix_part) + ":" + line
    return line

def main():
    parser = build_parser()
    args = parser.parse_args()

    regex_flags = re.IGNORECASE if args.ignore_case else 0

    try:
        regex = re.compile(args.pattern, regex_flags)

    except re.error as regexErr:
        print(f"Regex failed to compile with error: {regexErr}", file=sys.stderr)
        return 2
    
    anymatch = False
    
    filenames = list(iter_files(args.paths,args.include, args.exclude_dir))

    if not filenames:
        print("warning: no files to search", file=sys.stderr)
        return 1
    show_filenames = len(args.paths) > 1


    for filename in filenames:
        matched = search_paths(regex, filename, args.line_number, show_filenames, args.match_files_only)
        anymatch = anymatch or matched

    
    return 0 if anymatch else 1


if __name__ == "__main__":
    raise SystemExit(main())

