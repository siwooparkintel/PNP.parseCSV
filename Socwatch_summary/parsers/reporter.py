import csv
import time
import parsers.socwatch_summary_parser as soc
import parsers.pcie_socwatch_summary_parser as psoc



head_list = ["model_name"]

data_lines = []

data_vertical = []



def queryData(data_label) :
    data_line = None
    for line_index in range(len(data_lines)-1, -1, -1):
        line = data_lines[line_index]
        if data_label == line[0]:
            data_line = line
            break
    return data_line

def convertToVerticalData(data_lines) :
    data_vertical = list()
    for i in range(len(data_lines[0])) :
        rail_line = list()
        for j in range(len(data_lines)) :
            rail_line.append(data_lines[j][i])
        data_vertical.append(rail_line)
    return data_vertical

def addPowerRailsToHeader(head_list, power_list) :
    for key in power_list :
        head_list.append(key)

def addModelThroughputToHeader(head_list, AI_parsing_items) :
    # model_output = hobl_data[0]['model_output_obj']['model_output_data']
    for index in range(len(AI_parsing_items)) :
        key = AI_parsing_items[index]["key"]
        if key == "device" or key == "iterations":
            head_list.append(f"{key}")
        else :
            head_list.append(f"{key} ({AI_parsing_items[index]["unit"]})")

def etl_handler(block) :
    pass

def getTableByLabel(socwatch_tables, soc_key) :
    tbox = None
    for table in socwatch_tables :
        if soc_key == table['label'] :
            tbox = table
            break
    return tbox

def socwatch_handler(block, socwatch_targets, soc_header_dict) :
    data_line = queryData(block['data_label'])
    # print("=====pulled: ", block['data_label'], data_line)
    if data_line is not None:
        socwatch_tables = block['socwatch_obj']['socwatch_tables']
        # print("=====socwatch_tables: ", socwatch_tables)
        for soc_key in soc_header_dict :
            soc_head = soc_header_dict[soc_key]
            table = getTableByLabel(socwatch_tables, soc_key)
            buckets = next((item for item in socwatch_targets if item['key'] == soc_key and "buckets" in item), None)
            # print("=====pulled: ", soc_key, table)
            for s_key in soc_head :
                # print("== found buckets: ", soc_key, buckets)
                ranges = s_key.split("-")
                if table is not None and buckets is not None and len(ranges) == 2:
                    min = int(ranges[0])
                    max = int(ranges[1])
                    copied = table['table_data'].copy()
                    copied.pop(next(iter(copied)))
                    total = sum([float(copied[key]) for key in copied if int(key) >= min and int(key) <= max])
                    # print([float(copied[key]) for key in copied if int(key) >= min and int(key) <= max])
                    # print("== found buckets: ", table['table_data'], copied, ranges, total)
                    data_line.append(total)
                elif table is not None and s_key in table['table_data'] :
                    data_line.append(table['table_data'][s_key])
                else :
                    data_line.append(None)

def pcie_socwatch_handler(block, PCIe_targets, soc_header_dict) :
    data_line = queryData(block['data_label'])
    # print("=====pulled: ", block['data_label'], data_line)
    if data_line is not None:
        pcie_socwatch_tables = block['pcie_socwatch_obj']['pcie_socwatch_tables']
        # print("=====socwatch_tables: ", socwatch_tables)
        for soc_key in soc_header_dict :
            soc_head = soc_header_dict[soc_key]
            table = getTableByLabel(pcie_socwatch_tables, soc_key)
            buckets = next((item for item in PCIe_targets if item['key'] == soc_key and "buckets" in item), None)
            # print("=====pulled: ", soc_key, table)
            for s_key in soc_head :
                # print("== found buckets: ", soc_key, buckets)
                ranges = s_key.split("-")
                if table is not None and buckets is not None and len(ranges) == 2:
                    min = int(ranges[0])
                    max = int(ranges[1])
                    copied = table['table_data'].copy()
                    copied.pop(next(iter(copied)))
                    total = sum([float(copied[key]) for key in copied if int(key) >= min and int(key) <= max])
                    # print([float(copied[key]) for key in copied if int(key) >= min and int(key) <= max])
                    # print("== found buckets: ", table['table_data'], copied, ranges, total)
                    data_line.append(total)
                elif table is not None and s_key in table['table_data'] :
                    data_line.append(table['table_data'][s_key])
                else :
                    data_line.append(None)

def powerHandler(block, header) :
    data_line = [block["data_label"][0], block["data_label"][1]]
    power_obj = block["power_obj"]
    for key in power_obj['power_data']:
        data_line.append(power_obj['power_data'][key])
        if len(data_lines) == 0:
            header.append(key)
    return data_line

def powerOutputHandler(block, header) :
    # print("[powerOutputHandler::block] ", block)
    data_line = [block["data_label"], block["data_label"]]
    power_obj = block["power_obj"]
    for key in power_obj['power_data']:
        data_line.append(power_obj['power_data'][key])
        if len(data_lines) == 0:
            header.append(key)
    return data_line

def getSocwatchHeaderList(soc_dict) :
    soc_list = list()
    for key in soc_dict :
        soc_list.extend(soc_dict[key])
    return soc_list


def reportPickedData(file_path, hobl_data, socwatch_targets, PCIe_targets) :

    header = ['Condition', 'Name']  
    socwatch_header_dict = soc.getSocwatchHeader(socwatch_targets)
    pcie_socwatch_header_dict = psoc.getPcieSocwatchHeader(PCIe_targets)
    # print("[socwatch_header_dict] ", socwatch_header_dict)
    # print("[pcie_socwatch_header_dict] ", pcie_socwatch_header_dict)
    socwatch_blocks = list()

    for block in hobl_data :

        if "power_obj" in block:
            data_line = powerOutputHandler(block, header)
            # print("[data_line] ", data_line)
            data_lines.append(data_line)
        if "socwatch_obj" in block:
            socwatch_blocks.append(block)
    
    # extends socwatch parsed data here to make sure power data collected first
    for block in socwatch_blocks :
        socwatch_handler(block, socwatch_targets, socwatch_header_dict)
        pcie_socwatch_handler(block, PCIe_targets, pcie_socwatch_header_dict)
    
    socwatch_header = getSocwatchHeaderList(socwatch_header_dict)
    pcie_socwatch_hader = getSocwatchHeaderList(pcie_socwatch_header_dict)
    header.extend(socwatch_header)
    header.extend(pcie_socwatch_hader)
    data_lines.insert(0, header)

    # TODO : file extention handler goes here
    # file_names = file_path.split(".")
    # if len(file_names) > 1:
    #     extention = file_names[-1]
    #     upto_name = ".".join(file_names[0:-1])   

    with open(file_path+"_horizontal.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_lines)
    
    with open(file_path+"_vertical.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        data_vertical = convertToVerticalData(data_lines)
        writer.writerows(data_vertical)


def getTraceObject(hobl_data, DAQ_target) :
    block_list = list()
    for block in hobl_data :
        if "trace_obj" in block and "trace_data" in block["trace_obj"] and block["trace_obj"]["trace_data"] is not None :
            block_list.append(block)
            # return block["trace_obj"]["trace_data"]
    # print("============================ block_list: ", block_list)
    return block_list
        

def writeParsedInCSV(file_path, hobl_data, DAQ_target, socwatch_targets, PCIe_targets) :
    
    reportPickedData(file_path, hobl_data, socwatch_targets, PCIe_targets)


    




        


                



