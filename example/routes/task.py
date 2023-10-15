import re
import os
import json
import subprocess

from anyserver import WebRouter
from anyserver.utils.tracer import trace

# Define a router that we can load some routes into
router = WebRouter(prefix='/task')


def resolveTaskName(path, name=None):
    if name:
        return name
    match = re.search('^/task/([^\/|^?]*)', path)
    return match[1]


def RunCommand(cmd, env=os.environ.copy()):
    if not cmd:
        return None

    pop = cmd.split(" ")
    trace(' > Executes: %s' % cmd)
    res = subprocess.run(pop, stdout=subprocess.PIPE, env=env)
    output = res.stdout.decode().strip()

    return output


@router.get('/list')
def listTask(req, resp):
    return []

@router.post('/run')
def runTask(req, resp, ctx):
    # Collect the head and body
    body = req.body
    name = resolveTaskName(ctx.path)

    if not body:
        return resp.redirect(ctx, req.path)

    # Add HEAD and BODY values to ENV vars
    env = os.environ.copy()
    env["METHOD"] = ctx.command
    env["HEAD"] = json.dumps(req.head)
    env["BODY"] = json.dumps(req.body)

    # Execute the task command (given the input HEAD and BODY)
    output = RunCommand('task %s' % name, env)
    try:  # Parse output as JSON result
        data = json.loads(output)
    except:  # Fallback, send back raw text
        data = output
    return resp.reply(ctx, data)
