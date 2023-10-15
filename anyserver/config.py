
import os
import sys
import logging
import argparse

from anyserver.models.config import AnyConfig
from anyserver.encoders.core import Encoder


def GetConfig():
    opts = GetArgs()
    config = AnyConfig()

    # Try and load from config file (if specified)
    if opts.config and os.path.isfile(opts.config):
        configDict = Encoder.loadFile(opts.config)
        for key in configDict.keys():
            setattr(config, key, configDict[key])

    # Apply and load additional config settings
    ApplyArgs(config, opts)  # <-- Apply CLI args to config

    # Apply any CLI args and return the config
    return config


def GetArgs(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Extremely simple python server that can be easily be extended.'
    )

    # Core configurations and valiables used by all server types
    parser.add_argument('-c', '--config',
                        dest='config',
                        help='Specify your `config.yaml` file.',
                        )
    parser.add_argument('--host',
                        dest='host',
                        help='Specify the host we will bind the server to',
                        default='0.0.0.0'
                        )
    parser.add_argument('-p', '--port',
                        dest='port',
                        help='serve HTTP requests on specified port (default: 9999)',
                        type=int,
                        default=9999
                        )
    parser.add_argument('-w', '--working',
                        dest='working',
                        help='Specify the working directory',
                        default=os.getenv('WORK_DIR')
                        )

    # Allow the user to specify the type of server that will be created
    parser.add_argument('-s', '--static',
                        dest='static',
                        help='Static web contents to serve, if no other route defined',
                        # Default option: Serve current dir...
                        default=os.getenv('STATIC_DIR', '')
                        )
    parser.add_argument('--proxy',
                        dest='proxy',
                        help='Default route handler will reverse proxy to a URL'
                        )

    parser.add_argument('--debug',
                        help="Print debugging statements",
                        dest="debug",
                        action="store_const",
                        const=True,
                        default=False,
                        )
    parser.add_argument('--dev',
                        help="Start in development mode",
                        dest="development",
                        action="store_const",
                        const=True,
                        default=False,
                        )

    # Parse the args provided by the CLI
    args = parser.parse_args(argv)

    AnyConfig.debug = args.debug
    AnyConfig.is_dev = args.development

    # Set the log verbosity
    log_level = logging.WARN
    if args.debug:
        log_level = logging.DEBUG
    elif args.development:
        log_level = logging.INFO

    format = '%(message)s'
    logging.basicConfig(format=format, level=log_level)

    return args


def ApplyArgs(config, args):
    for key, val in vars(args).items():
        if val and key != "config":
            setattr(config, key, val)
    return config
