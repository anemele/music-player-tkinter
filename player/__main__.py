from .player import Player


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='The music directory')

    args = parser.parse_args()
    Player(args.dir).mainloop()


if __name__ == '__main__':
    main()
