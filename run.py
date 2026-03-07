from pathlib import Path
import logging

from utils import parse_args, Config
from shopping_platforms import PLATFORM_CLS

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def main() -> None:
    args = parse_args()
    config = Config.from_args(args)
    for p, items in config.p_items.items():
        platform = PLATFORM_CLS[p]()
        for item in items:
            transformed_data = platform.run(item)
            # TODO: db, check init schema, check tables, save data
            # TODO: alerter
            pass


if __name__ == "__main__":
    main()
