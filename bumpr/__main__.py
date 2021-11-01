import sys
from logging import DEBUG, INFO, getLogger


def main():
    from . import log

    log.init()

    from .config import Config, ValidationError
    from .helpers import BumprError
    from .releaser import Releaser

    config = Config.parse_args()
    getLogger().setLevel(DEBUG if config.verbose else INFO)
    logger = getLogger(__name__)

    try:
        config.validate()
    except ValidationError as e:
        msg = "Invalid configuration: {0}".format(e)
        logger.error(msg)
        sys.exit(1)

    try:
        releaser = Releaser(config)
        releaser.release()
    except BumprError as error:
        logger.error(str(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
