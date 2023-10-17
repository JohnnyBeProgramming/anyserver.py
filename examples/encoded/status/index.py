
import os
from anyserver.routers.templates import TemplateRouter

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Explicitly look in this directory for templates
router = TemplateRouter(base=f'{THIS_DIR}')


@router.get('/status')
@router.renders('index')  # Auto resolve extension, by accepted mimem types
def index(req, resp):
    return {
        "status": "online",
        "url": req.url,
    }
