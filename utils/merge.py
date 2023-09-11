#!/usr/bin/env python3
import os
import sys
import re

def main(argv=sys.argv[1:]):
    if not argv or not os.path.isfile(argv[0]): 
        print("You need to supply a valid python file as input arg.")
        return

    # Parse the input file and includes recursively
    input = argv[0]
    print('Merging contents of: %s' % input)
    base = os.path.dirname(input)
    parsed = parse(base, input)
    sep = "\n# + "
    includes = "# Included:" + sep + sep.join(parsed["head"].split("\n"))
    output = f"""{parsed["hash"]}
# ----------------------------
{parsed["head"]}
# ----------------------------
{parsed["body"]}
# ----------------------------
"""

    # Write the merged contents to file
    target = "./dist/server.py"
    dest = os.path.dirname(target)
    if len(argv) > 1: target = argv[1]
    if not os.path.isdir(dest): os.makedirs(dest)
    with open(target, "w") as file:
        file.write(output)

def find(input, pattern):
    match = re.search(pattern, input)
    if match: return match.string.split('\n')[0]
    return None

def parse(base, filename, state=None):    
    isRoot = not state
    if not state: state = {
            "hash": "",
            "head": "",
            "found": {},
            "body": ""
        }    
    with open(filename, "r") as file:
        input = file.read()

        # Extract the head info (if exists)
        match = find(input, "\#\!.+")
        if match and not state["hash"]: # extract head if exists
            input = input.replace(match+'\n', '') # Remove header from input
            state["hash"] = match
        
        # Try and parse imports
        pattern = re.compile(r'(from .*)?(import .*)\n')
        for line in re.findall(pattern, input):
            line = '%s%s' % line

            # Remove the import statement from the main input body
            input = input.replace(line+'\n', '')

            local = None            
            if match := re.search('from (.*) import (.*)', line):
                lib = match[1]

                # Determine relative file path
                path = lib.replace('.', '/')
                path = os.path.join(base, path)
                if os.path.exists(path + '.py'): 
                    # Local imports detected from a file matching the name
                    include(state, base, path + '.py')
                elif os.path.isdir(path):
                    # Local imports detected relative to a folder
                    for local in [path + '/' + x.strip() + '.py' for x in match[2].split(',')]:
                        if os.path.exists(local): include(state, base, local)
                else:
                    # This is most probably an non-local import
                    if not re.search(line+'\n', state["head"]): 
                        state["head"] = f'{state["head"]}\n{line}'.strip()
            elif match := re.search('import (.*)', line):
                # This is most likely a system import
                if not re.search(line+'\n', state["head"]): 
                    state["head"] = f'{state["head"]}\n{line}'.strip()
            
        # Return the merged content
        if isRoot:
            print('<= %s' % filename)
        else:
            print(' + %s' % filename)

        state["body"] = f'{state["body"]}\n\n{input}'.strip()
        return state

def include(state, base, local):
    # Add to headers as imported
    if not re.search(local+'\n', state["head"]): 
        state["head"] = f'{state["head"]}\n#import {local}'.strip()

    # If this is a local import, merge with current state
    if local and not local in state["found"]:
        state["found"][local] = True
        parse(base, local, state)

if __name__ == '__main__':
    main()