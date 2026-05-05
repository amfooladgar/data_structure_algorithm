#!/usr/bin/env python3
import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Search for a regex pattern in files."
    )

    parser.add_argument("pattern")
    parser.add_argument("paths", nargs="+")

    parser.add_argument(
        "-n",
        "--line-number",
        action="store_true",
        help="Show the line number for each match",
    )

    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Search case-insensitively",
    )

    parser.add_argument(
        "-l",
        "--files-with-matches",
        action="store_true",
        help="Print only the filename once if the file contains at least one match",
    )

    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Skip excluded directory names. May be passed multiple times.",
    )

    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Only search files whose basename matches this glob. May be passed multiple times.",
    )

    return parser


def should_include_file(path, include_globs):
    if not include_globs:
        return True

    basename = Path(path).name
    return any(fnmatch.fnmatch(basename, glob) for glob in include_globs)


def iter_paths(raw_paths, exclude_dirs, include_globs):
    for raw_path in raw_paths:
        path = Path(raw_path)

        if path.is_file():
            if should_include_file(path, include_globs):
                yield path

        elif path.is_dir():
            for root, dirnames, filenames in os.walk(path):
                dirnames[:] = [
                    dirname for dirname in dirnames
                    if dirname not in exclude_dirs
                ]

                for filename in filenames:
                    file_path = Path(root) / filename

                    if file_path.is_file() and should_include_file(file_path, include_globs):
                        yield file_path

        else:
            print(f"psearch: {path}: no such file or directory", file=sys.stderr)


def search_file(path, regex, show_filename, show_line_number, files_with_matches):
    found = False

    try:
        with open(path, mode="r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                if regex.search(line):
                    found = True

                    if files_with_matches:
                        print(path)
                        return True

                    prefix_parts = []

                    if show_filename:
                        prefix_parts.append(str(path))

                    if show_line_number:
                        prefix_parts.append(str(line_number))

                    if prefix_parts:
                        prefix = ":".join(prefix_parts)
                        print(f"{prefix}:{line}", end="")
                    else:
                        print(line, end="")

    except OSError as err:
        print(f"psearch: {path}: {err}", file=sys.stderr)

    return found


def main(argv=None):
    parser = parse_args()
    args = parser.parse_args(argv)

    regex_flags = re.IGNORECASE if args.ignore_case else 0

    try:
        regex = re.compile(args.pattern, regex_flags)
    except re.error as err:
        print(f"psearch: invalid regex: {err}", file=sys.stderr)
        return 2

    exclude_dirs = set(args.exclude_dir)
    include_globs = args.include

    show_filename = (
        len(args.paths) > 1
        or any(Path(raw_path).is_dir() for raw_path in args.paths)
    )

    any_match = False

    for path in iter_paths(args.paths, exclude_dirs, include_globs):
        matched = search_file(
            path=path,
            regex=regex,
            show_filename=show_filename,
            show_line_number=args.line_number,
            files_with_matches=args.files_with_matches,
        )
        any_match = any_match or matched

    return 0 if any_match else 1


if __name__ == "__main__":
    raise SystemExit(main())