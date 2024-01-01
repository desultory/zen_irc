#!/usr/bin/env python3


from .zenircclient import ZenIRCClient
from argparse import ArgumentParser
from logging import getLogger, StreamHandler
from zenlib.logging import ColorLognameFormatter


def main():
    parser = ArgumentParser(prog="crackbot")

    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug loggin')
    parser.add_argument('-dd', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-c', '--config', type=str, help='Config file')

    args = parser.parse_args()

    logger = getLogger('ZenIRCClient')
    if args.verbose:
        logger.setLevel(5)
        formatter = ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s')
    elif args.debug:
        logger.setLevel(10)
        formatter = ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s')
    else:
        logger.setLevel(20)
        formatter = ColorLognameFormatter()

    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    kwargs = {'logger': logger}

    if args.config:
        kwargs['config'] = args.config

    ZenIRCClient(**kwargs)


if __name__ == "__main__":
    main()
