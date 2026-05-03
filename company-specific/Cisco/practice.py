import sys
import argparse
import re

def search_file(regex, file, show_filename, show_linenumber):
    found = False
    # opening the file
    #check if the pattern is available
    # print according to the input options

    try:
        with open(file=file, mode='r', encoding='utf-8', errors='replace') as f:
            for line_number, line in enumerate(f, start=1):
                if regex.search(line):
                    found = True
                    prefix_part = []
                    if show_filename:
                        prefix_part.append(file)
                    if show_linenumber:
                        prefix_part.append(str(line_number))
                    
                    if prefix_part:
                        print(":".join(prefix_part) + ":" + line, end="")
                    else:
                        print(line, end="")
    except OSError as osErr:
        print(f"error in reading file {file}: {osErr}", file=sys.stderr)

    return found

def main():
    parser = argparse.ArgumentParser(
        description="search based on the pattern in a file content"
    )
    parser.add_argument("pattern") 
    parser.add_argument('files', nargs="+")
    
    # Add argument options such as -n, -i, -l, etc here

    parser.add_argument("-n","--line-number", action="store_true", help="")
    parser.add_argument("-i","--ignore-case", action="store_true", help="")

    args = parser.parse_args()
    regex_flags = re.IGNORECASE if args.ignore_case else 0

    try:
        regex = re.compile(args.pattern, regex_flags)
    except re.error as reErr:
        print(f"error while compiling regex for pattern {args.pattern}: {reErr}", file=sys.stderr)
        return 2
    
    show_filename = len(args.files)>1
    anymatch = False

    for filename in args.files:
        matched = search_file(regex, filename, show_filename, args.line_number)
        anymatch = anymatch or matched
    
    return 0 if anymatch else 1
    




if __name__=="__main__":
    raise SystemExit(main())