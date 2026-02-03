#!/usr/bin/env python3
import os
import sys

SUFFIX = '.md'


def read_authors(filenm: str) -> dict:
    authors = {}
    with open(filenm) as f:
        for line in f:
            authors[line.rstrip()] = False
    return authors


def author_has_file(authors: dict, dir_to_check: str) -> dict:
    os.chdir(dir_to_check)
    print(f"Current working directory changed to: {os.getcwd()}")
    files = os.listdir('.') # '.' refers to the current directory
    for file in files:
        stripped = file.replace(SUFFIX, '')
        if stripped in authors:
            authors[stripped] = True
    return authors


def main():
    if len(sys.argv) < 3:
        print('USAGE: missing.py [author_file] [dir_to_check]')
        exit(1)
    author_file = sys.argv[1]
    dir_to_check = sys.argv[2]
    authors = read_authors(author_file)
    authors = author_has_file(authors, dir_to_check)
    for author in authors:
        if not authors[author]:
            print(f'{author} is missing in {dir_to_check}')


if __name__ == '__main__':
    main()
