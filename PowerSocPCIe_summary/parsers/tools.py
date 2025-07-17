import re
import sys


def parseNumeric(text) :
    return ''.join(re.findall(r'[0-9.]', text))
def parseDevice(text) :
    return ''.join(re.findall(r'[A-Z.0-9]', text))

def splitLastItem(abs_path, joint, cutNum) :
    item_list = abs_path.split(joint)
    return [joint.join(item_list[:-cutNum]), item_list[len(item_list)-1]]

def trim_list(data_list):
    """
    Removes empty items from the back of a list.
    An item is considered 'empty' if it evaluates to False (e.g., '', 0, None, [], {}).
    """
    while data_list and data_list[-1].strip() == "":  # Check if list is not empty and last element is falsy
        data_list.pop()
    return [item.strip() for item in data_list]

def errorAndExit(msgs) :
    print("=============================================================================")
    sys.exit("[Error] :: " + msgs)
    print("=============================================================================")
