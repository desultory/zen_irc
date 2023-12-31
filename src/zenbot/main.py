#!/usr/bin/env python3


from zenbot import ZenBot
from argparse import ArgumentParser
from logging import getLogger, StreamHandler
from zenlib.logging import ColorLognameFormatter


def main():
    parser = ArgumentParser(prog="crackbot")

    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug loggin')
    parser.add_argument('-dd', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-c', '--config', type=str, help='Config file')

    args = parser.parse_args()

    logger = getLogger('ZenBot')
    handler = StreamHandler()
    handler.setFormatter(ColorLognameFormatter())
    logger.addHandler(handler)

    if args.verbose:
        logger.setLevel(5)
    elif args.debug:
        logger.setLevel(10)
    else:
        logger.setLevel(20)

    kwargs = {'logger': logger}

    if args.config:
        kwargs['config'] = args.config

    bot = ZenBot(**kwargs)
    bot.run()


if __name__ == "__main__":
    main()
