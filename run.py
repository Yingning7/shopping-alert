import logging

from shopping_platforms import PLATFORM_CLS
from utils import parse_args, Config
from database import Database

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)


def main() -> None:
    logger.info("Running shopping alert.")
    args = parse_args()
    config = Config.from_args(args)
    database = Database()
    for platform_name, platform_config in config.platforms_configs.items():
        logger.info(f"Running platform: {platform_name.value}.")
        platform = PLATFORM_CLS[platform_name]()
        for args in platform_config["run_args"]:
            transformed_data = platform.run(args)
            database.insert_data(transformed_data)
    database.close()
    logger.info("Finished running shopping alert.")


if __name__ == "__main__":
    main()
