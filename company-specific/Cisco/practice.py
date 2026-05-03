#!/usr/bin/env python3

import argparse
import os
import re
import sys
from pathlib import Path
import fnmatch

def should_include_file(filepath, include_pattern):

    if include_pattern is None:
        return True
    return fnmatch.fnmatch(filepath,include_pattern)


def iter_files(paths, include_pattern, excluded_dirs):
    # Iterate over every path passed by the user.
    for raw_path in paths:
        # Convert string path into a Path object.
        path = Path(raw_path)

        # If this path is a file, yield it directly.
        if path.is_file():
            if should_include_file(path, include_pattern):
                yield path

        # If this path is a directory, walk it recursively.
        elif path.is_dir():
            for root, dirnames, filenames in os.walk(path):
                # For every file in this directory level...
                dirnames[:] = [
                    dirname for dirname in dirnames
                    if dirname not in excluded_dirs
                ]

                for filename in filenames:
                    # Build the full file path.
                    filepath = Path(root) / filename
                    if should_include_file(filepath, include_pattern):
                        yield filepath

        # If path is neither file nor directory, warn and continue.
        else:
            print(f"warning: path does not exist: {path}", file=sys.stderr)


def search_file(
    regex,
    file_path,
    show_filename,
    show_line_number,
    files_with_matches,
):
    found = False

    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                if regex.search(line):
                    found = True

                    if files_with_matches:
                        print(file_path)
                        return True

                    prefix_parts = []

                    if show_filename:
                        prefix_parts.append(str(file_path))

                    if show_line_number:
                        prefix_parts.append(str(line_number))

                    if prefix_parts:
                        print(":".join(prefix_parts) + ":" + line, end="")
                    else:
                        print(line, end="")

    except OSError as exc:
        print(f"warning: could not read {file_path}: {exc}", file=sys.stderr)

    return found


def main():
    parser = argparse.ArgumentParser(
        description="Search for a regex pattern in files and directories."
    )

    parser.add_argument("pattern")

    # These can now be files or directories.
    parser.add_argument("paths", nargs="+")

    parser.add_argument("-n", "--line-number", action="store_true")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("-l", "--files-with-matches", action="store_true")
    parser.add_argument("--include", help="example: --include=*.log")
    parser.add_argument("--exclude-dir", action="append", default=[], help="example: --exclude-dir=/usr/. Directory name to skip. Can be passed multiple times.")

    args = parser.parse_args()

    regex_flags = re.IGNORECASE if args.ignore_case else 0

    try:
        regex = re.compile(args.pattern, regex_flags)
    except re.error as exc:
        print(f"error: invalid regex: {exc}", file=sys.stderr)
        return 2

    # Expand files and directories into a list of files.
    files = list(
        iter_files(args.paths,
                 include_pattern=args.include, 
                 excluded_dirs=args.exclude_dir
                 ))

    if not files:
        print("warning: no files to search", file=sys.stderr)
        return 1

    # Prefix filename when more than one actual file is searched.
    show_filename = len(files) > 1

    any_match = False

    for file_path in files:
        matched = search_file(
            regex=regex,
            file_path=file_path,
            show_filename=show_filename,
            show_line_number=args.line_number,
            files_with_matches=args.files_with_matches,
        )
        any_match = any_match or matched

    return 0 if any_match else 1


if __name__ == "__main__":
    raise SystemExit(main())