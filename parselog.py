#! /usr/local/bin/python

#------------------------------------------------------------------------------
# Copyright (C) 2009 James Brooks (kerspoon)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

"""
A program to parse a PSAT results file and say if it's in limits.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys 
import optparse
import logging
from os.path import basename, splitext

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
    format="%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  
#------------------------------------------------------------------------------
class EndofFile(Exception):
    pass

def nextline(stream):
    return stream.next()

def forward_to_line(stream, line):
    for stline in stream:
        if line == stline:
            return

def SimInLimits(stream, simtype):

    if simtype == "powerflow":
        if nextline(stream) != "POWER FLOW REPORT\n":
            logger.info("fail: incorrect title")
            return False

    elif simtype == "optimalpowerflow":
        if nextline(stream) != "OPTIMAL POWER FLOW REPORT\n":
            logger.info("fail: incorrect title")
            return False
    else:
        raise Exception("bad call to function 'check'")

    try:
        forward_to_line(stream, 'LIMIT VIOLATION STATISTICS\n')
    except EndofFile:
        logger.info("fail: missing limits section")
        return False

    inlimits = True

    if simtype == "powerflow":
        inlimits &= nextline(stream).startswith("ALL VOLTAGES WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL REACTIVE POWER WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL CURRENT FLOWS WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL REAL POWER FLOWS WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL APPARENT POWER FLOWS WITHIN LIMITS")
    elif simtype == "optimalpowerflow":
        inlimits &= nextline(stream).startswith("ALL VOLTAGES WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL REACTIVE POWERS WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL CURRENT FLOWS WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL REAL POWER FLOWS WITHIN LIMITS")
        inlimits &= nextline(stream).startswith("ALL APPARENT POWER FLOWS WITHIN LIMITS")
    else:
        raise Exception("bad call to function 'check'")
        
    if not inlimits:
        logger.info("fail: out of limits")
        return False

    logger.info("pass")
    return True

#------------------------------------------------------------------------------
#  "main2" function:
#------------------------------------------------------------------------------

def main2(infile, outfile, simtype):
    if SimInLimits(infile, simtype):
        print "Pass"
    else:
        print "Fail"

#------------------------------------------------------------------------------
#  "main" function:
#------------------------------------------------------------------------------

def main():
    """ Parses the command line and call with the correct in/out.
    """
    parser = optparse.OptionParser("usage: parselog [options] input_file")

    parser.add_option("-t", "--type", dest="simtype", default="powerflow",
        help="read as a PSAT 'powerflow' or 'optimalpowerflow'")

    parser.add_option("-o", "--output", dest="output", metavar="FILE",
        help="Write the solution report to FILE.")

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="Print less information.")

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
        default=False, help="Print debug information.")

    (options, args) = parser.parse_args()

    if options.quiet:
        logger.info("setting logger level to critical")
        logger.setLevel(logging.CRITICAL)
    elif options.debug:
        logger.info("setting logger level to debug")
        logger.setLevel(logging.DEBUG)
    else:
        logger.info("setting logger level to info")
        logger.setLevel(logging.INFO)

    # Output.
    if options.output:
        outfile = options.output
        if outfile == "-":
            outfile = sys.stdout
            logger.info("logger level set to critical as output is to stdout")
            logger.setLevel(logging.CRITICAL) # we must stay quiet
    else:
        outfile = sys.stdout
        logger.info("logger level set to critical as output is to stdout")
        logger.setLevel(logging.CRITICAL) # we must stay quiet

    # Input.
    if len(args) > 1:
        parser.print_help()
        sys.exit(1)
    elif len(args) == 0 or args[0] == "-":
        infilename = ""
        if sys.stdin.isatty():
            # True if the file is connected to a tty device, and False
            # otherwise (pipeline or file redirection).
            parser.print_help()
            sys.exit(1)
        else:
            # Handle piped input ($ cat ehv3.raw | pylon | rst2pdf -o ans.pdf).
            infile = sys.stdin
    else:
        infilename = args[0]
        infile   = open(infilename)

    logger.info("Running Program with: %s" % infilename)
    logger.info("===================")
    main2(infile, outfile, options.simtype)
    logger.info("===================")

if __name__ == "__main__":
    main()


# EOF -------------------------------------------------------------------------
