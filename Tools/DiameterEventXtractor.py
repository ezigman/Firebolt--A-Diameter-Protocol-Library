import os
import sys
import optparse

import firebolt.Utils.DiameterUtils as utils


def start_parsing(options):
    if not options.inputFile:
        print "ERROR: Input diameter file not specified."
        return False

    try:
        fd = open(options.inputFile, "rb")
    except Exception, e:
        print "ERROR: {0}".format(str(e))
        return False

    fileSize = os.path.getsize(options.inputFile)
    try:
        [part_1, ext] = os.path.basename(options.inputFile).split('.')
    except Exception, e:
        print "Provide some extension to the file: {0}".format(str(e))
        sys.exit(1)

    startPos = 0

    nFd = open(part_1 + "_xtract.{0}".format(ext), "wb")

    ## Go till the position
    while True:
        curSize = fd.tell()

        if fileSize == curSize:
            break

        # Read first 4 bytes of diameter event(which is part of 20 byte header)
        [msgLen, _version] = utils.getFlagAndLength(fd.read(4))

        # move back by 4 bytes
        fd.seek(-4, 1)
        data = fd.read(msgLen)
        startPos += 1

        if startPos >= options.start_pos:
            if startPos < (options.start_pos + options.number):
                nFd.write(data)

    fd.close()
    nFd.close()

    return True


def print_options(options):
    print "Input File Name    : {0}".format(options.inputFile)
    print "Output File Name   : {0}".format(options.outputFile)
    print "Starting position  : {0}".format(options.start_pos)
    print "Number of events   : {0}".format(options.number)



def main():
    parser = optparse.OptionParser()

    parser.add_option( '-i', '--inputFile',
                        action = "store",
                        dest = "inputFile",
                        help = "Input diameter file."
                     )

    parser.add_option( '-o', '--outputFile',
                        action = "store",
                        dest = 'outputFile',
                        default = None,
                        help = "Output File name having extracted events."
                     )

    parser.add_option( '-s', '--start',
                        action = "store",
                        dest = "start_pos",
                        type = "int",
                        default = 1,
                        help = "Starting position from where events needs to be extracted(Position of 1st event is 1)."
                     )

    parser.add_option( '-n', '--number',
                        action = "store",
                        dest = "number",
                        type = "int",
                        default = 1,
                        help = "Number of events to extract"
                     )

    options, remainder = parser.parse_args()

    print_options(options)

    if start_parsing(options):
        print "Extraction completed..."
    else:
        print "Extraction failed."

    return True



if __name__ == "__main__":
    main()    
