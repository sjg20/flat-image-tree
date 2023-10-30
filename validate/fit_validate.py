#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0+

"""Flat Image Tree validator

Written by Simon Glass <sjg@chromium.org>

This does not use dtschema, at least for now, since it does not have bindings
for FIT.
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
        fit (lifdt.Fdt): FDT to validate
        fail (list of str): List of failures
    """
    def __init__(self, fname):
        self.fname = fname
        self.fit = None
        self.fail = []

    def add_fail(self, msg):
        """Add a new failure to the list

        Args:
            msg (str): Message describing the failure
        """
        self.fail.append(msg)

    def show_results(self):
        """Show the results of validation"""
        if self.fail:
            print('FAIL')
            for warn in self.fail:
                print(warn)
        else:
            print('PASS')

    def check_fdt(self):
        try:
            with open(self.fname, 'rb') as inf:
                self.fit = libfdt.Fdt(inf.read())
                return True
        except libfdt.FdtException as exc:
            self.add_fail(f'Not a valid FDT file {exc}')
            return False

    def check_root(self):


    def validate(self):
        """Perform validation of the current file"""
        if not self.check_fdt():
            return
        self.check_root()


def validate_file(fname):
    """Validate a file

    Args:
        fname (str): Filename to validate
    """
    val = Validator(fname)
    val.validate()
    val.show_results()

def run_fit_validate():
    """Run the program"""
    args = parse_args()
    for fname in args.files:
        validate_file(fname)


if __name__ == "__main__":
    sys.exit(run_fit_validate())
