
import sys
from models.episode import Episode


def main() -> int:
    episode = Episode()
    episode.run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
