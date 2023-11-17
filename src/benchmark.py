
from models.episode import Episode
import sys


def main(agent) -> int:
    score = 0
    for _ in range(1000):
        print("New episode...")
        episode = Episode(False)
        score += episode.run(agent)

        print("Episode finished.\n\n")

    print("================================")
    print(f"score: {score}")
    print("================================")


if __name__ == '__main__':
    main(sys.argv[1])
