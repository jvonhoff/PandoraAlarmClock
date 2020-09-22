#!/usr/bin/env python

import os
import sys
from os.path import expanduser, join

path = os.environ.get('XDG_CONFIG_HOME')
if not path:
    path = expanduser("~/.config")
else:
    path = expanduser(path)
fn = join(path, 'pianobar', 'nowplaying')

info = sys.stdin.readlines()
cmd = sys.argv[1]

if cmd == 'songstart':
    with open(fn, 'w') as f:
        f.write("".join(info))

