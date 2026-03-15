from pathlib import Path
import logging

from shopping_platforms import PlatformName, PLATFORM_CLS_SELECTOR
from utils import parse_args, load_platform_configs
from database import Database

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)


def main() -> None:
    logger.info("Running shopping alert.")
    cmd_args = parse_args()
    platforms_configs = load_platform_configs(Path(__file__).parent / "configs/platforms.toml")
    platforms_to_run = [PlatformName(cmd_args.platform)] if cmd_args.platform != "all" else list(PlatformName)
    database = Database()
    for platform_name in platforms_to_run:
        logger.info(f"Running platform: {platform_name.value}.")
        platform_config = platforms_configs[platform_name.value]
        platform_cls = PLATFORM_CLS_SELECTOR[platform_name]
        platform = platform_cls()
        for run_args in platform_config["run_args"]:
            try:
                transformed_data = platform.run(run_args)
            except Exception as error:
                logger.error(f"Failed to run platform: {platform_name.value}. Error: {error}. Run args: {run_args}.")
                continue
            database.insert_data(transformed_data)
    database.close()
    logger.info("Finished running shopping alert.")


if __name__ == "__main__":
    main()
