import argparse

from trapperkeeper import models
from trapperkeeper import config

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create schema on configured database.")
    parser.add_argument("-c", "--config", default="/etc/trapperkeeper.yaml",
                        help="Path to config file.")
    args = parser.parse_args()

    config = config.Config.from_file(args.config, False)

    db_engine = models.get_db_engine(config["database"])
    models.Model.metadata.create_all(db_engine)
