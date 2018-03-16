#!/usr/bin/env python
# Copyright (c) 2018, Kontron Europe GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import argparse
import copy
import json
import matplotlib.pyplot as plt
import sys
import threading
import time


def update_histogram(json, output):
    histogram = output['object']
    histogram['count'] += 1

    latency_usec = json['latency-user-hw'] / 1000
    if latency_usec > histogram['max'] or histogram['max'] == 0:
        histogram['max'] = latency_usec
    if latency_usec < histogram['min'] or histogram['min'] == 0:
        histogram['min'] = latency_usec

    if latency_usec < 0:
        histogram['time_error'] += 1
    elif latency_usec < len(histogram['histogram']):
        histogram['histogram'][latency_usec] += 1
    else:
        histogram['outliers'] += 1


def main(args=None):
    parser = argparse.ArgumentParser(
        description='histogen')
    parser.add_argument('-c', '--count', type=int, dest='count', default=0)
    parser.add_argument('--width', type=int, dest='width', default=100)
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                       default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                       default=sys.stdout)
    args = parser.parse_args(args)

    output = None
    histogram_empty = {
        'type': 'histogram',
        'object': {
            'count': 0,
            'min': 0,
            'max': 0,
            'outliers': 0,
            'time_error': 0,
            'histogram': [0] * args.width,
        }
    }

    histogram_out = copy.deepcopy(histogram_empty)

    count = 0
    try:
        for line in args.infile:
            try:
                j = json.loads(line)
                if j['type'] == 'latency':
                    update_histogram(j['object'], histogram_out)

                    if args.count != 0:
                        count += 1

                        if count == args.count:
                            print(json.dumps(histogram_out), file=sys.stdout)
                            sys.stdout.flush()
                            count = 0
                            histogram_out = copy.deepcopy(histogram_empty)

            except ValueError:
                pass
    except KeyboardInterrupt as e:
        pass

    if output == None:
        print(json.dumps(histogram_out), file=sys.stdout)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
