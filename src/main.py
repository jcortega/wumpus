
import sys
from models.episode import Episode


def main(mode, debug) -> int:
    episode = Episode(debug)

    if mode == 'naive':
        episode.run_naive_agent()
    elif mode == 'human':
        episode.run()

    return 0


if __name__ == '__main__':
    mode = sys.argv[1]
    try:
        debug = sys.argv[2] == "debug"
    except:
        debug = False
        pass

    sys.exit(main(mode, debug))
