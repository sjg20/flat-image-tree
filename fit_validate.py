#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0+

"""Flat Image Tree validator

Written by Simon Glass <sjg@chromium.org>
"""

import argparse
import sys

import libfdt

def parse_args():
    """Parse arguments to the program

    Returns:
        Namespace: Parsed arguments
    """
    epilog = 'Validate Flat Image Tree (FIT) files'
    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument('files', type=str, nargs='*', help='Files to validate')
    # parser.add_argument('-U', '--show-environment', action='store_true',
          # default=False, help='Show environment changes in summary')

    return parser.parse_args()


class Validator:
    """Validates Flat Image Tree files

    Checks that the required nodes and properties are present, makes sure that
    invalid nodes and properties are not present.

    Properties:
        fname (str): Filename being validated
    """
    def __init__(self, fname):
        self.fname = fname

    def validate(self):
        """Perform validation of the current file"""


def validate_file(fname):
    """Validate a file

    Args:
        fname (str): Filename to validate
    """
    with open(fname, 'rb') as inf:
        fit = libfdt.Fdt(inf.read())
        val = Validator(fit)
        val.validate()


def run_fit_validate():
    """Run the program"""
    args = parse_args()
    for fname in args.files:
        validate_file(fname)


if __name__ == "__main__":
    sys.exit(run_fit_validate())
