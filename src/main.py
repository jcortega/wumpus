
import sys
from models.episode import Episode


def main(debug) -> int:
    episode = Episode(debug)
    episode.run()

    return 0


if __name__ == '__main__':
    try:
        debug = sys.argv[1] == "debug"
    except:
        debug = False
        pass

    sys.exit(main(debug))
