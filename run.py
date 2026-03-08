import logging

from shopping_platforms import PLATFORM_CLS
from utils import parse_args, Config
from database import Database

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def main() -> None:
    args = parse_args()
    config = Config.from_args(args)
    database = Database()
    for platform_name, platform_config in config.platforms_configs.items():
        platform = PLATFORM_CLS[platform_name]()
        for args in platform_config["run_args"]:
            transformed_data = platform.run(args)
            pass


if __name__ == "__main__":
    main()
