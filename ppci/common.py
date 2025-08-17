"""
Error handling routines
Diagnostic utils
Source location structures
"""

import logging
from pathlib import Path
from .lang.common import SourceLocation


logformat = "%(asctime)s | %(levelname)8s | %(name)10.10s | %(message)s"


def make_num(txt):
    if txt.startswith("0x"):
        return int(txt[2:], 16)
    elif txt.startswith("-0x"):
        return -int(txt[3:], 16)
    elif txt.startswith("$"):
        return int(txt[1:], 16)
    elif txt.startswith("0b"):
        return int(txt[2:], 2)
    elif txt.startswith("%"):
        return int(txt[1:], 2)
    else:
        return int(txt)


str2int = make_num


def get_file(f, mode="r"):
    """Determine if argument is a file like object or make it so!"""
    if hasattr(f, "read"):
        # Assume this is a file like object
        return f
    elif isinstance(f, Path):
        return f.open(mode)
    elif isinstance(f, str):
        return open(f, mode)
    else:
        raise FileNotFoundError(f"Cannot open {f}")


class CompilerError(Exception):
    def __init__(self, msg, loc=None, hints=None):
        # super().__init__()
        self.msg = msg
        self.loc = loc
        if loc:
            issue = f"{type(loc)} must be SourceLocation"
            assert isinstance(loc, SourceLocation), issue

        if hints is None:
            hints = []
        self.hints = hints

    def __repr__(self):
        return f'"{self.msg}"'

    def render(self, lines):
        """Render this error in some lines of context"""
        self.loc.print_message(f"Error: {self.msg}", lines=lines)
        for hint in self.hints:
            print(hint)

    def print(self, file=None):
        """Print the error inside some nice context"""
        if self.loc and self.loc.filename:
            self.loc.print_message(self.msg, file=file)
        else:
            print(self.msg, file=file)

        for hint in self.hints:
            print(hint)


class IrFormError(CompilerError):
    pass


class ParseError(CompilerError):
    pass


class DiagnosticsManager:
    def __init__(self):
        self.diags = []
        self.sources = {}
        self.logger = logging.getLogger("diagnostics")

    def add_source(self, name, src):
        """Add a source for error reporting"""
        self.logger.debug('Adding source, filename="%s"', name)
        self.sources[name] = src

    def add_diag(self, d):
        """Add a diagnostic message"""
        if d.loc:
            self.logger.error("Line %s: %s", d.loc.row, d.msg)
        else:
            self.logger.error(str(d.msg))
        self.diags.append(d)

    def error(self, msg, loc):
        self.add_diag(CompilerError(msg, loc))

    def clear(self):
        del self.diags[:]
        self.sources.clear()

    def print_errors(self):
        """Print all errors reported"""
        if len(self.diags) > 0:
            print(f"{len(self.diags)} Errors")
            for d in self.diags:
                self.print_error(d)

    def print_line(self, row, lines):
        """Print a single source line"""
        if row in range(len(lines)):
            txt = lines[row - 1]
            print(f"{row:5}:{txt}")

    def print_error(self, e):
        """Print a single error in a nice formatted way"""
        print("==============")
        if e.loc:
            if e.loc.filename not in self.sources:
                print(f"Error: {e}")
                return
            print(f"File: {e.loc.filename}")
            source = self.sources[e.loc.filename]
            lines = source.split("\n")
            e.render(lines)
        else:
            print(f"Error: {e}")

        print("==============")
