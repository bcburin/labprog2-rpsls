import logging


def configure_logger(filename: str, level=logging.INFO, mode='a'):
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(
                filename=filename,
                mode=mode
            ),
            logging.StreamHandler()
        ]
    )
