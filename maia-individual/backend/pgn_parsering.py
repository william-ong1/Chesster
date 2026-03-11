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

        # Skip blank lines between games
        while True:
            l = self.f.readline()
            if not l:
                raise StopIteration
            self.i += 1
            if len(l) >= 2:
                break

        # Parse headers until blank line
        while True:
            lines += l
            try:
                k, v, _ = l.split('"')
            except ValueError:
                if l == 'null\n':
                    pass
                else:
                    raise
            else:
                ret[k[1:-1]] = v

            l = self.f.readline()
            if not l:
                raise StopIteration
            self.i += 1
            if len(l) < 2:
                if len(ret) < 2:
                    raise RuntimeError(l)
                # Blank line between headers and movetext
                lines += l
                break

        # Read full movetext until next blank line (Chess.com PGNs split moves over many lines)
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
