import csv
import time
import parsers.socwatch_summary_parser as soc
import parsers.power_trace_parser as ptp


head_list = ["model_name"]

data_lines = []

data_vertical = []



def queryData(data_label_list) :
    data_line = None
    for line_index in range(len(data_lines)-1, -1, -1):
        line = data_lines[line_index]
        if data_label_list[0] == line[0] and data_label_list[1] == line[1] :
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

def powerHandler(block, header) :
    data_line = [block["data_label"][0], block["data_label"][1]]
    power_obj = block["power_obj"]
    for key in power_obj['power_data']:
        data_line.append(power_obj['power_data'][key])
        if len(data_lines) == 0:
            header.append(key)
    return data_line

def powerOutputHandler(block, header) :
    data_line = [block["data_label"][0], block["data_label"][1]]
    power_obj = block["power_obj"]
    for key in power_obj['power_data']:
        data_line.append(power_obj['power_data'][key])
        if len(data_lines) == 0:
            header.append(key)
    if "model_output_obj" in block:
        output_data = block["model_output_obj"]['model_output_data']
        for key in output_data:
            data_line.append(output_data[key][0])
            if len(data_lines) == 0:
                header.append(key)
    return data_line

def getSocwatchHeaderList(soc_dict) :
    soc_list = list()
    for key in soc_dict :
        soc_list.extend(soc_dict[key])
    return soc_list

def reportAllPowerAndType(file_path, hobl_data) :
    # header = ['Condition', 'Name']
    allPowerData = [["Condition"],["Name"]]

    # getting header from the first data, adding "picked" if not there
    if "power_obj" in hobl_data[0] and "power_data" in hobl_data[0]["power_obj"] :
        for key in hobl_data[0]["power_obj"]["power_data"] :
            allPowerData.append([key])
    allPowerData.append(["power_type"])
    allPowerData.append(["picked"])
    allPowerData.append(["file_path"])

    # print(allPowerData)
    for rail_list in allPowerData :
        for block in hobl_data :
            if "power_obj" in block and "power_data" in block["power_obj"] : 
                if rail_list[0] == "Condition":
                    rail_list.append(block["data_label"][0])
                elif rail_list[0] == "Name":
                    rail_list.append(block["data_label"][1])
                elif rail_list[0] == "power_type":
                    rail_list.append(block["power_obj"]["power_type"])
                elif rail_list[0] == "picked":
                    rail_list.append(block["power_obj"]["picked"] if "picked" in block["power_obj"] else None)
                elif rail_list[0] == "file_path":
                    rail_list.append(block["power_obj"]["file_path"])
                else :
                    rail_list.append(block["power_obj"]["power_data"][rail_list[0]] if rail_list[0] in block["power_obj"]["power_data"] else None)

    with open(file_path+"_"+"all_powers.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(allPowerData)


def reportPickedData(file_path, hobl_data, socwatch_targets) :

    header = ['Condition', 'Name']  
    socwatch_header_dict = soc.getSocwatchHeader(socwatch_targets)
    socwatch_blocks = list()

    for block in hobl_data :

        if "power_obj" in block and "picked" in block["power_obj"]:

            if "ETL" in block["data_type"] :
                etl_handler(block)
            elif  "socwatch_obj" in block:
                socwatch_blocks.append(block)
                # socwatch_handler(block, socwatch_targets, socwatch_header_dict)
            else :
                data_line = powerOutputHandler(block, header)
                # inf_data_line = infOnlyPowerHandler(block, header) if data_line is not None and picks["inferencing_power"] else None

                similar_model_index = None
                for index in range(len(data_lines)-1, -1, -1):
                    if data_lines[index][1].find(data_line[1]) >= 0:
                        similar_model_index = index
                        break
                if similar_model_index is not None :
                    data_lines.insert(similar_model_index+1, data_line)
                else : 
                    data_lines.append(data_line)
    
    # extends socwatch parsed data here to make sure power data collected first
    for block in socwatch_blocks :
        socwatch_handler(block, socwatch_targets, socwatch_header_dict)
    
    socwatch_header = getSocwatchHeaderList(socwatch_header_dict)
    header.extend(socwatch_header)
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
        

def reportInforencingOnlyPower(file_path, hobl_data, DAQ_target):
    start_time = time.perf_counter()

    inf_only_lines = list()
    ptp.averageInferencingPower(hobl_data, DAQ_target)

    header = ["Condition","Name"]
    trace_blocks = getTraceObject(hobl_data, DAQ_target)

    for key in trace_blocks[0]["trace_obj"]["trace_data"] :
        header.append(key)

    header.append("file_path")  

    # for rail_list in allPowerData :
    for block in trace_blocks :
        trace_data = block["trace_obj"]["trace_data"]
        trace_line = [block["data_label"][0], block["data_label"][1]]
        for key in header :
            if key == "file_path" :
                trace_line.append(block["trace_obj"][key])
            elif key in trace_data :
                trace_line.append(trace_data[key])
        

        similar_model_index = None
        for index in range(len(inf_only_lines)-1, -1, -1):
            if inf_only_lines[index][1].find(trace_line[1]) >= 0:
                similar_model_index = index
                break
        if similar_model_index is not None :
            inf_only_lines.insert(similar_model_index+1, trace_line)
        else : 
            inf_only_lines.append(trace_line)
        # inf_only_lines.append(trace_line)
    inf_only_lines.insert(0, header)

    # ====== directly write it as vertical data format
    # for rail_list in allPowerData :
    #     for block in trace_blocks :
    #         if rail_list[0] == "Condition":
    #             rail_list.append(block["data_label"][0])
    #         elif rail_list[0] == "Name":
    #             rail_list.append(block["data_label"][1])
    #         elif rail_list[0] == "file_path":
    #             rail_list.append(block["trace_obj"]["file_path"])
    #         else :
    #             rail_list.append(block["trace_obj"]["trace_data"][rail_list[0]] if rail_list[0] in block["trace_obj"]["trace_data"] else None)

    with open(file_path+"_"+"Infer_Power_h.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(inf_only_lines)

    with open(file_path+"_"+"Infer_Power_v.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        data_vertical = convertToVerticalData(inf_only_lines)
        writer.writerows(data_vertical)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"{len(trace_blocks)} of Detecting and Calculate inferencing only Power from trace raw data [Elapsed time:::] {elapsed_time} seconds")


def writeParsedInCSV(file_path, hobl_data, socwatch_targets, DAQ_target) :
    
    reportAllPowerAndType(file_path, hobl_data)
    reportPickedData(file_path, hobl_data, socwatch_targets)
    reportInforencingOnlyPower(file_path, hobl_data, DAQ_target)


    




        


                



