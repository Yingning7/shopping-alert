import logging

from shopping_platforms import PLATFORM_CLS
from utils import parse_args, Config

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def main() -> None:
    args = parse_args()
    config = Config.from_args(args)
    for platform, items in config.platform_items.items():
        platform = PLATFORM_CLS[platform]()
        for item in items:
            transformed_data = platform.run(item)
            # TODO: db, check init schema, check tables, save data
            # TODO: alerter
            pass


if __name__ == "__main__":
    main()
