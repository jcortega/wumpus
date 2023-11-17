
import sys
from models.episode import Episode


def main(mode, debug) -> int:
    episode = Episode(debug)

    score = episode.run(mode)

    print("Total score for this episode: ", score)

    return 0


if __name__ == '__main__':
    mode = sys.argv[1]
    try:
        debug = sys.argv[2] == "debug"
    except:
        debug = False
        pass

    sys.exit(main(mode, debug))
