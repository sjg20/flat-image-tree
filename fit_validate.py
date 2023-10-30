#!/usr/bin/env python3

# Flat Image Tree validator
# Written by Simon Glass <sjg@chromium.org>

import argparse

def parse_args():
    epilog = 'Validate Flat Image Tree (FIT) files'
    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument('FILES', type=str, nargs='*', help='Files to validate')
    # parser.add_argument('-U', '--show-environment', action='store_true',
          # default=False, help='Show environment changes in summary')

    return parser.parse_args()


def run_fit_validate():
    return


if __name__ == "__main__":
    sys.exit(run_fit_validate())
