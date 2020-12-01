#!/usr/bin/python

# This file is used to test whether calling a python script from Vocareum's student view is possible or not.
# Sample source taken from https://www.tutorialspoint.com/python/python_command_line_arguments.htm

import getopt
import sys


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is ', inputfile)
    print('Output file is ', outputfile)

    print("Writing to output file!")
    with open(outputfile, 'w') as file:
        file.write(f"Assignment Score, 15")
    print("Output written!")


if __name__ == "__main__":
    main(sys.argv[1:])
