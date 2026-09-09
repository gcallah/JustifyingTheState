#!/usr/bin/env python3

# Read the file order.txt
# Read all of the files in the keywords directory
# Assemble all of the keywords into a single file with the format:
#    chap02_callahan: followed by the keywords from the file
#    ./keywords/callahan.md
# The output should go to: ./submission/keywords.txt

# Implement a program according to the above specification.

def read_order_file(order_file_path):
    with open(order_file_path, 'r') as f:
        order = [line.strip() for line in f.readlines()]
    return order


def read_keywords_file(keywords_file_path):
    with open(keywords_file_path, 'r') as f:
        keywords = [line.strip() for line in f.readlines()]
    return keywords


def assemble_keywords(order, keywords_dir):
    assembled_keywords = []
    for chap_no, name in enumerate(order, start=1):
        keywords_file_path = f"{keywords_dir}/{name}.md"
        keywords = read_keywords_file(keywords_file_path)
        assembled_keywords.append(f"chap{chap_no:02d}_{name}: {' '.join(keywords)}")
    return assembled_keywords


def write_output_file(output_file_path, assembled_keywords):
    with open(output_file_path, 'w') as f:
        for line in assembled_keywords:
            f.write(line + '\n')


def main():
    order_file_path = './order.txt'
    keywords_dir = './keywords'
    output_file_path = './submission/keywords.txt'

    order = read_order_file(order_file_path)
    assembled_keywords = assemble_keywords(order, keywords_dir)
    write_output_file(output_file_path, assembled_keywords)


if __name__ == "__main__":
    main()
