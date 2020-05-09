#! [license info here]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########
# translates the flat/unstructured JSON commit data into a commit history (directed acyclic graph [DAG])
##########

##########
# Import libraries
##########
import networkx as nx
import seaborn as sns

def build_commit_history(known_commits, commit_history):

    
    """
    TODO: Add docstring. See: https://realpython.com/documenting-python-code/
    TODO: Implement recursion argument, default to False.

    Parameters
    ==========

    `known_commits` : list of dicts, required, input of this function, commit data generated by perceval in the function get_commit.py
    `commit_history` : networkx DiGraph, required, output of this function, empty container for the commit history 
 
    Raises
    ======

    NotImplementedError
        If no sound is set for the animal or passed in as a
        parameter.
    """
    
    # ------------------------------------------------------------
    # first pass: add all nodes
    for commit in known_commits:

        # add the current node to the network
        commit_history.add_node(commit['commit'][:7],
                   commit=commit['commit'],
                   shortSha=commit['commit'][:7],
                   Author=commit['Author'],
                   AuthorDate=commit['AuthorDate'],
                   Commit=commit['Commit'],
                   CommitDate=commit['CommitDate'],
                   message=commit['message'],
                   refs=commit['refs'],
                   parents=commit['parents']
                   )    
        
    # ------------------------------------------------------------
    # second pass: create links
    for commit in known_commits:
 
        # link the commit with their parents
        for parent_sha in commit['parents']:
            commit_history.add_edge(parent_sha[:7], commit['commit'][:7])

    # ------------------------------------------------------------
    # third pass: identify which commit belongs to which branch
 
    # each git branch reference commit (those where the variable 'refs' is not empty)
    branch_heads = [x for x in commit_history.nodes() if len(commit_history.nodes[x]['refs'])!=0]

    # container to store all found branch names (needed for colourizing later)
    branch_names = list()

    for branch_head in branch_heads:

        # fetch the contents of the 'refs' variable containing the branch name(s)
        refs = commit_history.nodes[branch_head]['refs']
        parents = commit_history.nodes[branch_head]['parents']

        # there must be the same number of parents and branch refs 
        if len(refs)!=len(parents):
            raise Exception
        else:
            # add the attribute 'branch' to the current node and propagate it upwards in the DAG
            for i in range(len(refs)):
                # if the name contains 'refs/heads/', then the ref is a branch ref (could be a release ref (in this case it would conain*refs/tags*))
                if 'refs/heads/' in refs[i]:
                    
                    # we add the branch to our list of known branch names (needed for colourizing later)
                    branch_names.append(refs[i])

                    commit_history.nodes[branch_head]['branch'] = refs[i]
                    # if the parent is a branch head, we stop here
                    if len(commit_history.nodes[parents[i][:7]]['refs']) == 0:
                        # if branch info has already been added to the parent, we stop here as well
                        if not 'branch' in commit_history.nodes[parents[i][:7]]:
                            propagate_branch_name(commit_history, parents[i][:7], refs[i])

    # ------------------------------------------------------------
    # fourth pass: colorize

    # define as many colours as branches
    palette = sns.color_palette("hls", len(branch_names)) # returns a rgb tuple normalzed in [0,1]
    palette_html = list()
    for colour_tuple in palette: # convert the palette to HTML format
        html_colour_code = '#'
        for colour_code in colour_tuple:
            html_colour_code = html_colour_code + '%02x' % int(round(colour_code*256))
        palette_html.append(html_colour_code) 

    for commit in commit_history.nodes():

        # fetch a colour
        colour = palette_html[branch_names.index(commit_history.nodes[commit]['branch'])]

        # set node colour based commit's branch index
        commit_history.nodes[commit]['colour'] = colour

        # set outward edges colour based commit's branch index
        for neighbour in commit_history[commit]: # 'commit_history[commit]' returns a subgraph of 'commit_history' with neighbours of 'commit'
            commit_history.edges[commit, neighbour]['colour'] = colour

##########
# finds out which commit belongs to which branch
##########

def propagate_branch_name(commit_history, commit, branch):
    commit_history.nodes[commit]['branch'] = branch
    for parent_sha in commit_history.nodes[commit]['parents']:
        # if the parent is a branch head, we stop here
        if not 'refs/heads/' in ''.join(commit_history.nodes[parent_sha[:7]]['refs']):
            # if branch info has already been added to the parent, we stop here as well
            if not 'branch' in commit_history.nodes[parent_sha[:7]]:
                propagate_branch_name(commit_history, parent_sha[:7], branch)

