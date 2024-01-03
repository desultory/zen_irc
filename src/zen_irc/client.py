#!/usr/bin/env python3


from .zenircclient import ZenIRCClient
from .zenircgui import ZenIRCGUI
from zenlib.logging import ColorLognameFormatter

from PyQt6.QtWidgets import QApplication
from argparse import ArgumentParser
from logging import getLogger, StreamHandler
from asyncio import run as run_asyncio


def parse_args():
    parser = ArgumentParser(prog="zen_irc_client", description="Zen IRC Client")

    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-dd', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-c', '--config', type=str, help='Config file')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')

    return parser.parse_args()


def get_logger(args):
    logger = getLogger('ZenIRCClient')
    handler = StreamHandler()

    if args.verbose:
        logger.setLevel(5)
        formatter = ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s')
    elif args.debug:
        logger.setLevel(10)
        formatter = ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s')
    else:
        logger.setLevel(20)
        formatter = ColorLognameFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    args = parse_args()
    logger = get_logger(args)

    kwargs = {'logger': logger}

    if args.config:
        kwargs['config'] = args.config

    if args.cli:
        client = ZenIRCClient(**kwargs)
        client.start()
    run_asyncio(main_async(kwargs))


async def main_async(kwargs):
    app = QApplication([])
    gui = ZenIRCGUI(**kwargs)
    await gui.client.start()
    app.exec()


if __name__ == "__main__":
    main()
