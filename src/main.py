from agent import AgentBrain
from world import WumpusWorld


def main():
    world = WumpusWorld()
    world.load('map/world2.txt')

    agent = AgentBrain(world, output_file=None, verbose=True)

    agent.solve()


if __name__ == '__main__':
    main()
