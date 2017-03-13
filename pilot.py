#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Mario Lassnig, mario.lassnig@cern.ch, 2016-2017

import argparse
import logging
import sys

from pilot.util.constants import SUCCESS, ERRNO_NOJOBS

VERSION = '2017-03-06.001'


def main():
    logger = logging.getLogger(__name__)
    logger.info('pilot startup - version {0} '.format(VERSION))

    logger.info('workflow: {0}'.format(args.workflow))
    workflow = __import__('pilot.workflow.{0}'.format(args.workflow), globals(), locals(), [args.workflow], -1)
    return workflow.run(args)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-d',
                            dest='debug',
                            action='store_true',
                            default=False,
                            help='enable debug logging messages')

    # the choices must match in name the python module in pilot/workflow/
    arg_parser.add_argument('-w',
                            dest='workflow',
                            default='generic',
                            choices=['generic', 'generic_hpc',
                                     'production', 'production_hpc',
                                     'analysis', 'analysis_hpc',
                                     'eventservice', 'eventservice_hpc'],
                            help='pilot workflow (default: generic)')

    # graciously stop pilot process after hard limit
    arg_parser.add_argument('-l',
                            dest='lifetime',
                            default=10,
                            type=int,
                            help='pilot lifetime seconds (default: 10)')

    # set the appropriate site and queue
    arg_parser.add_argument('-s',
                            dest='site',
                            required=True,
                            help='MANDATORY: site name (e.g., AGLT2)')
    arg_parser.add_argument('-r',
                            dest='resource',
                            required=True,
                            help='MANDATORY: resource name (e.g., AGLT2_TEST)')
    arg_parser.add_argument('-q',
                            dest='queue',
                            required=True,
                            help='MANDATORY: queue name (e.g., AGLT2_TEST-condor')

    args = arg_parser.parse_args()

    console = logging.StreamHandler(sys.stdout)
    if args.debug:
        logging.basicConfig(filename='pilotlog.txt', level=logging.DEBUG,
                            format='%(asctime)s | %(levelname)-8s | %(threadName)-10s | %(name)-32s | %(funcName)-32s | %(message)s')
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(threadName)-10s | %(name)-32s | %(funcName)-32s | %(message)s'))
    else:
        logging.basicConfig(filename='pilotlog.txt', level=logging.INFO,
                            format='%(asctime)s | %(levelname)-8s | %(message)s')
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
    logging.getLogger('').addHandler(console)

    trace = main()
    logging.shutdown()

    if trace.pilot['nr_jobs'] > 0:
        sys.exit(SUCCESS)
    else:
        sys.exit(ERRNO_NOJOBS)