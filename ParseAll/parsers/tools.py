import re
import sys


def parseNumeric(text) :
    return ''.join(re.findall(r'[0-9.]', text))
def parseDevice(text) :
    return ''.join(re.findall(r'[A-Z.0-9]', text))

# add def saveLastOpenedFolder(folder_path):
def saveLastOpenedFolder(folder_path):
    try:
        with open("./src/last_opened_folder.txt", "w") as f:
            f.write(folder_path)
    except Exception as e:
        print(f"Failed to save last opened folder: {e}")

def tryRoundifNumber(value) :
    try :
        return round(float(value), 2)
    except ValueError as e:
        return value

def tryIntifNumber(value) :
    try :
        return int(value)
    except ValueError as e:
        return value
        
def splitLastItem(abs_path, joint, cutNum) :
    item_list = abs_path.split(joint)
    return [joint.join(item_list[:-cutNum]), item_list[len(item_list)-1]]

def find_dict_by_key_value(data, key, value):
    for item in data:
        if item.get(key) == value:
            return item
    return None

def trim_list(data_list):
    """
    Removes empty items from the back of a list.
    An item is considered 'empty' if it evaluates to False (e.g., '', 0, None, [], {}).
    """
    while data_list and data_list[-1].strip() == "":  # Check if list is not empty and last element is falsy
        data_list.pop()
    return [item.strip() for item in data_list]

def flatten_model_dic(entry) :
    
    if "model_output_obj" in entry and "model_output_data" in entry["model_output_obj"] :
        copied = entry["model_output_obj"]['model_output_data'].copy()
        new_output = dict()
        for index, key in enumerate(copied):
            value_list = copied[key]
            updated_key = key+f" ({value_list[1]})" if value_list[1] is not "" else key
            new_output[updated_key] = value_list[0]
        new_output['model_output_path'] = entry["model_output_obj"]["model_output_path"]
        return new_output
    else :
        return {}

def flatten_power_dic(entry, picks):
    if "power_obj" in entry and "power_data" in entry["power_obj"] :
        copied = entry["power_obj"]['power_data'].copy()
        copied["power_type"] = entry['power_obj']['power_type']
        copied[picks['power_pick']+"_picked"] = entry['power_obj']['picked']
        copied["power_path"] = entry['power_obj']['file_path']
        return copied
    else :
        return {}
    
def flatten_trace_dic(entry):
    if "trace_obj" in entry and "trace_data" in entry["trace_obj"] :
        copied = entry["trace_obj"]['trace_data'].copy()
        copied["total_row"] = entry['trace_obj']['total_row']
        copied["duration_in_scale"] = entry['trace_obj']['duration_in_scale']
        copied["inf_start"] = entry['trace_obj']['inf_start']
        copied["inf_end"] = entry['trace_obj']['inf_end']
        copied["file_path"] = entry['trace_obj']['file_path']
        return copied
    else :
        return {}
        
def flatten_socwatch_dic(entry, socwatch_targets):
    if "socwatch_obj" in entry and "socwatch_tables" in entry["socwatch_obj"] :
        flat_socwatch = {}
        for table in entry["socwatch_obj"]["socwatch_tables"]:
            # flat_socwatch.update(table["table_data"]) if "table_data" in table else {}

            data = table["table_data"]
            if "bucketized_data" in table:
                data = table["bucketized_data"]
            for item in data :
                # print(item, item+"_"+table["label"])
                flat_socwatch[item+"        "+table["label"]] = data[item]
            # flat_socwatch[table]
        flat_socwatch['socwatch_path'] = entry['socwatch_obj']['socwatch_path']
        return flat_socwatch
    else :
        return {}

def flatten_pcie_socwatch_dic(entry, pcie_socwatch_targets):
    if "pcie_socwatch_obj" in entry and "pcie_socwatch_tables" in entry["pcie_socwatch_obj"] :
        flat_socwatch = {}
        for table in entry["pcie_socwatch_obj"]["pcie_socwatch_tables"]:
            # flat_socwatch.update(table["table_data"]) if "table_data" in table else {}

            data = table["table_data"]
            if "bucketized_data" in table:
                data = table["bucketized_data"]
            for item in data :
                # print(item, item+"_"+table["label"])
                flat_socwatch[item+"        "+table["label"]] = tryRoundifNumber(data[item])
            # flat_socwatch[table]
        flat_socwatch['pcie_socwatch_path'] = entry['pcie_socwatch_obj']['pcie_socwatch_path']
        return flat_socwatch
    else :
        return {}
        
def errorAndExit(msgs) :
    print("=============================================================================")
    sys.exit("[Error] :: " + msgs)
    print("=============================================================================")
