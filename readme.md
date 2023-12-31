# Zen IRC

A simple python IRC client library

## Installing

This repo can be cloned, and the project can be installed with `pip install .`

## Handlers

When a certain IRC command is received, a function named `handler_{command}` is executed, where the tokenized message is passed.

## Commands

Functions in the `commands.py` file are imported, and are used as aliases for running IRC commands
