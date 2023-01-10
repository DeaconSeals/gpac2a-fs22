#!/usr/bin/python3

# author: Deacon Seals

# use: python3 treeCheck.py treeFilePath0 treeFilePath1 ... treeFilePathN
# use note: Bash regex filename expressions supported

import sys
import re # python regex library


def get_depth(line):
    # trying to support arbitratry node strings was a mistake
    return len(line) - len(line.lstrip("|")) # this is kinda gross but it works

'''
desc:   Returns the number of children for a node on a given line.
'''
def num_children(depths, line_num):
    my_depth = depths[line_num]
    children = 0
    for line in range(line_num+1, len(depths)):
        node_depth = depths[line]
        if node_depth == my_depth+1:
            children += 1
        elif node_depth <= my_depth:
            break
    return children

'''
desc:   Checks tree file at input `filepath` for a valid tree. Considers formatting errors
        that cause tree depth to increase by unreasonable amounts, the number of children
        each node has. A comment is made for each instance of an unknown node, but this 
        does not indicate an error if the node is a new sensor or operator you have added
        and documented.
'''
def check_tree(filename):
    sensors = {"G", "P", "W", "F"}
    operators = {"+":2, "-":2, "*":2, "/":2, "RAND":2}

    # identified sensor nodes
    def is_sensor(value):
        numbers = value.split(".")
        return value in sensors or re.fullmatch('(-?[0-9]+(\.[0-9]*)?)', value)

    errors = []
    tree_text = []

    with open(filename, 'r') as file:
        tree_text = [line.rstrip() for line in file] # remove tailing space from each line
    # remove tailing blank lines from file
    for line in range(len(tree_text)):
        if tree_text[-(line+1)]:
            if line > 0:
                tree_text = tree_text[:-line]
            break
    if not tree_text:
        print(filename + ": [ERROR] is empty")
        return

    depths = [get_depth(line) for line in tree_text]
    nodes = [line.lstrip("|") for line in tree_text]
    children = [num_children(depths, line) for line in range(len(tree_text))]

    # check for invalid depth increases
    for line in range(len(tree_text)-1):
        if depths[line+1]-depths[line] > 1:
            errors.append("depth increased by more than 1 between lines " \
                            + repr(line+1) + " and " + repr(line+2))
    
    # somewhat abusive way of breaking if we've already found errors
    if [print(filename + ": [ERROR] " + error) for error in errors]: return

    for line in range(len(tree_text)):
        node = nodes[line]
        num_kids = children[line]
        if is_sensor(node): # sensor
            if num_kids != 0: # sensor has children but shouldn't
                errors.append("sensor node " + repr(node) + " on line " + repr(line+1) \
                                + " has " + repr(num_kids) + " more children than it should")
        elif node in operators: # operators
            if num_kids != operators[node]: # defined operator has incorrect number of children
                errors.append("operator node " + repr(node) + " on line " + repr(line+1) \
                                + " has " + repr(num_kids) + " children but " + \
                                repr(operators[node]) + " were expected")
        else: # unknown node
            print(filename + ": [warning] unknown node " + repr(node) + " on line " \
                            + repr(line+1) + " has " + repr(num_kids) + " children")

    # print errors or pass
    if not [print(filename + ": [ERROR] " + error) for error in errors]: # still a little hacky
        print(filename + ": PASS")
    return

def main():
    if len(sys.argv) < 2:
        print("Please pass in a world file")
    else:
        for arg in range(1, len(sys.argv)):
            check_tree(sys.argv[arg])

if __name__ == '__main__':
    main()