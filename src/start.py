#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt

import json

try:
    from get_Github_forks import get_Github_forks
except:
    print("Need `get_Github_forks.py`")
    exit(1)

try:
    from get_commits import get_commits
except:
    print("Need `get_commits.py`")
    exit(1)

def main():
    # get command line arguments
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'u:r:t:', [
                                           'user=', 'repo=', 'token='])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    # initialise the parameters to be found in the arguments
    username = ''
    repo = ''
    token_path = ''

    for option, argument in options:
        if option in ('-u', '--user'):
            username = argument
        if option in ('-r', '--repo'):
            repo = argument
        if option in ('-t', '--token'):
            token_path = argument
 
    # check whether all required parameters have been given as arguments and if not throw exception and abort
    if username == '':
        print ("Argument required: GitHub username. Type '-u <username>' in the command line")
        sys.exit(2)
    if repo == '':
        print ("Argument required: GitHub repository. Type '-r <filepath>' in the command line")
        sys.exit(2)
    if token_path == '':
        print ("Argument required: OAuth token file. Type '-t <directory path>' in the command line")
        sys.exit(2)

    print("User: " + username)
    print("Repository: " + repo)
    print("Token file: " + token_path)
    #
    # Get Github personal access token
    #

    auth = dict()

    try:
        with open(file=token_path, mode="r") as token_file:
            token_items = token_file.read().split(sep="\n")
            auth["login"] = token_items[0]
            auth["secret"] = token_items[1]
            del(token_file, token_items)
    except FileNotFoundError as token_error:
        print("Can't find or open Github API access token file.\n" + + str(token_error))
        exit(2)

    forks = list()
    forks.append({'user': username,
                'repo': repo,
                'parent_user': username,
                'parent_repo': repo})

    get_Github_forks(username=username, reponame=repo, forks=forks, auth=auth)

    # JB 2020 05 03 - BEGIN
    # Commented saving a json file with fork references
    # we don't need a file anymore since we used directly the fork references to fetch commits
    # forks_json = json.dumps(forks, sort_keys=True, indent=4)
    # output_file = repo + ".json"
    # save the Perceval docs to a file
    # with open(output_file, 'w') as f:
    #     f.write(forks_json)
    # JB 2020 05 03 - END

    for fork in forks:
        print("retrieving commits in " + fork['user'] + "/" + fork['repo'])
        commits = list()
        get_commits(username=fork['user'], reponame=fork['repo'], commits=commits)
        output_JSON = '../__DATA__/JSON_commits/' + fork['user'] + '-' + fork['repo'] + '.json'
        # convert commits to a JSON string for export
        commits_JSON = json.dumps(commits, sort_keys=True, indent=4)
        # save the commits to a file
        with open(output_JSON, 'w') as f:
           f.write(commits_JSON)
        del f
        
        # this reloads the commits from the exported file
        #with open(output_JSON, 'r') as f:
        #    content = f.read()
        #    commits = json.loads(content)


if __name__ == "__main__":
    main()
