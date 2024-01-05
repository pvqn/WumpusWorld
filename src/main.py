import sys
from agent import AgentBrain
from world import WumpusWorld


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    world = WumpusWorld()
    world.load(input_path)

    output_file = open(output_path, 'w')

    agent = AgentBrain(world, output_file=output_file, verbose=True)

    agent.solve()

    output_file.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 main.py <input_path> <output_path>')
        exit(1)

    main()
