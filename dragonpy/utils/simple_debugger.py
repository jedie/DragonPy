#!/usr/bin/env python

"""
    borrowed from http://code.activestate.com/recipes/52215/

    usage:

    try:
        # ...do something...
    except:
        print_exc_plus()
"""


import sys
import traceback

import click


MAX_CHARS = 256


def print_exc_plus():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    sys.stderr.flush()  # for eclipse
    sys.stdout.flush()  # for eclipse

    tb = sys.exc_info()[2]
    while True:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back

    txt = traceback.format_exc()
    txt_lines = txt.splitlines()
    first_line = txt_lines.pop(0)
    last_line = txt_lines.pop(-1)
    click.secho(first_line, fg="red")
    for line in txt_lines:
        if line.strip().startswith("File"):
            click.echo(line)
        else:
            click.secho(line, fg="white", bold=True)
    click.secho(last_line, fg="red")

    click.echo()
    click.secho(
        "Locals by frame, most recent call first:",
        fg="blue", bold=True
    )
    for frame in stack:
        msg = f'File "{frame.f_code.co_filename}", line {frame.f_lineno:d}, in {frame.f_code.co_name}'
        msg = click.style(msg, fg="white", bold=True, underline=True)
        click.echo(f"\n *** {msg}")

        for key, value in list(frame.f_locals.items()):
            click.echo("%30s = " % click.style(key, bold=True), nl=False)
            # We have to be careful not to cause a new error in our error
            # printer! Calling str() on an unknown object could cause an
            # error we don't want.
            if isinstance(value, int):
                value = f"${value:x} (decimal: {value:d})"
            else:
                value = repr(value)

            if len(value) > MAX_CHARS:
                value = f"{value[:MAX_CHARS]}..."

            try:
                click.echo(value)
            except BaseException:
                click.echo("<ERROR WHILE PRINTING VALUE>")
