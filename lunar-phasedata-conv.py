#!/usr/bin/env python3

import argparse
import logging
import pathlib
import json

log = logging.getLogger()

def convert_phasedata(filename: str):
    log.debug(f'Convert {filename}')

    phasedata = pathlib.Path(filename).read_text()
    phases = json.loads(phasedata)

    bydate = dict()

    for phase in phases["phasedata"]:
        log.debug(f'Phase: {phase}')
        d = f'{phase["year"]}-{phase["month"]:02d}-{phase["day"]:02d}'
        p = phase["phase"]
        phasec = ''
        match p:
            case 'Full Moon':
                phasec = '○'
            case 'New Moon':
                phasec = '●'
            case 'First Quarter':
                phasec = '◐'
            case 'Last Quarter':
                phasec = '◑'

        bydate[d] = {"phase": p, "c": phasec}

    print(json.dumps(bydate))

def main():
    log = logging.getLogger()

    parser = argparse.ArgumentParser(
        prog='lunar-phasedata-conv',
        description='Convert data from USN Lunar Phase data',
        epilog='')

    parser.add_argument('filename')
    parser.add_argument('-d', '--debug', default=False, action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)


    if args.filename:
        convert_phasedata(args.filename)

if __name__ == '__main__':
    main()
