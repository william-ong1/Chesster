import re
import bz2

import chess.pgn

moveRegex = re.compile(r'\d+[.][ \.](\S+) (?:{[^}]*} )?(\S+)')

class GamesFile(object):
    def __init__(self, path):
        if path.endswith('bz2'):
            self.f = bz2.open(path, 'rt')
        else:
            self.f = open(path, 'r')
        self.path = path
        self.i = 0

    def __iter__(self):
        try:
            while True:
                yield next(self)
        except StopIteration:
            return

    def __del__(self):
        try:
            self.f.close()
        except AttributeError:
            pass

    def __next__(self):
        ret = {}
        lines = ''
        for l in self.f:
            self.i += 1
            lines += l
            if len(l) < 2:
                if len(ret) >= 2:
                    break
                else:
                    raise RuntimeError(l)
            else:
                try:
                    k, v, _ = l.split('"')
                except ValueError:
                    if l == 'null\n':
                        pass
                    elif len(ret) >= 2:
                        break  # no " in line: missing blank before movetext (e.g. cleaned.pgn)
                    else:
                        raise
                else:
                    ret[k[1:-1]] = v
        # Read full movetext until next blank line (was: only 2 readlines; Chess.com splits over many lines)
        while True:
            nl = self.f.readline()
            if not nl:
                break
            self.i += 1
            if len(nl) < 2:
                break
            lines += nl
        if len(lines) < 1:
            raise StopIteration
        return ret, lines
