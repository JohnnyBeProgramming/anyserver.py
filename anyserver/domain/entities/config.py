

class AnyConfig:
    # Host configuration
    host = '0.0.0.0'
    port = 9999

    # Define the target folders
    working = "."
    templates = "./templates"
    static = None  # eg: ./public

    # Runtime settings
    debug = False
    is_dev = False
    discover = True
    entrypoint = None
    routes = {}
    proxy = None
