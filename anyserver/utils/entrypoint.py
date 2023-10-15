
import inspect
import logging
import os
import re


class Entrypoint():
    found = None
    debug = False

    @staticmethod
    def get():
        def debug(msg): return logging.debug(msg) if Entrypoint.debug else None

        if Entrypoint.found:
            return Entrypoint.found

        debug(f'Finding entrypoint from stack trace... {Entrypoint.found}')
        stack = inspect.stack()
        for frame in stack:
            if not len(frame) > 5:
                continue

            path = frame[1]
            desc = frame[3]
            line = frame[4][0].strip() if len(frame[4]) else ''
            debug(f' * [ {desc} ] {path} <-- ({line})')

            if desc == '<module>':
                if res := re.search(r'(.*) = (.*)', line):
                    file = os.path.basename(path)
                    base = os.path.splitext(file)[0]
                    property = res.groups()[0] if res else None
                    entrypoint = f'{base}:{property}'
                    Entrypoint.found = entrypoint
                    debug(f' < entrypoint: {entrypoint} --  {line}')
                    return entrypoint

        return None
