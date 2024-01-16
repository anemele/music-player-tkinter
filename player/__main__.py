import sys

if len(sys.argv) == 1:
    print('Not given the music directory')
    exit(1)
from .player import Player

Player(sys.argv[1]).mainloop()
