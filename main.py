from config import ConfigManager
from suite import Suite


def main():
    config = ConfigManager.load("config.yaml")
    Suite(config).run()


if __name__ == "__main__":
    main()
