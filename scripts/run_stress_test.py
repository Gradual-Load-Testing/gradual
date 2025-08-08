from gevent import monkey

monkey.patch_all()
import pathlib
from argparse import ArgumentParser
from gradual.base.orchestrator import Orchestrator
from logging import getLogger, INFO

logger = getLogger()
logger.setLevel(INFO)

parser = ArgumentParser()
parser.add_argument(
    "--test_config",
    type=pathlib.Path,
    required=True,
    help="Path to the test configuration file",
)
parser.add_argument(
    "--request_config", type=pathlib.Path, help="Path to the request configuration file"
)
args = parser.parse_args()

orchestrator = Orchestrator(args.test_config, args.request_config)
orchestrator.start_stress_test()
