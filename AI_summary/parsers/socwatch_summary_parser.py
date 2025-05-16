# Socwatch Options:
# Command line options: -s 0 -o c:\hobl_data\socwatch\AI_GPU_model_stripped -f temp -f npu -f gfx -f memss-pstate -f cpu-cstate -f hw-cpu-hwp -f hw-cpu-cstate -f hw-cpu-pstate -f os-cpu-cstate -f os-cpu-pstate -f hw-igfx-cstate -f hw-igfx-pstate -f display-state -f ddr-bw -f bw-all -f noc-pstate -f media-pstate -m -r auto --no-post-processing 


socwatch_header_dict = dict()

def cpuModelTable(table) :
    copied = table['table_data'].copy()
    data = dict()
    for line in copied:
        items = line[0].split("=")
        if len(items) > 1 :
            key = items[0].split("/")[1].strip()
            data[key] = items[-1].strip()
    table['table_data'] = data

def oneLineColonSeperater(table) :
    copied = table['table_data'].copy()
    data = dict()
    for line in copied:
        items = line[0].split(":")
        data[items[0]] = items[-1].strip()
    table['table_data'] = data 

def tempAvrTable(table): 
    copied = table['table_data'].copy()
    data = {table['label']:copied[0][4]}
    for index in range(1, len(copied), 1):
        line = copied[index]
        data[line[0].split("/")[-1]] = line[4]
    table['table_data'] = data 

def bwTotalAvr(table) :
    num = len(table['table_data'])
    # table['table_data'] = {table['table_data'][0][2]:table['table_data'][num-1][2]}
    table['table_data'] = {table['label']+"_AvrRt(MB/s)":table['table_data'][num-1][2]}

def coreFreqResidencyTable(table, core_type_dict):
    copied = table['table_data'].copy()
    header_start = copied[0][0]
    data = {header_start:[]}
    if core_type_dict is not None :
        for TYPE in core_type_dict : 
            core_name = core_type_dict[TYPE]
            if core_name not in data[header_start]:
                data[header_start].append(core_name)
    # print("=== in coreFreqResidencyTable: ", header_start, core_type_dict)

    header = copied[0][2:]
    top_bin = copied[1][2:]
    
    for index in range(1, len(copied), 1) :  # this is exccluding freq 0, idle. : for index in range(1, len(copied)-1, 1) :
        row = copied[index]
        line_dict = dict()
        line_data_only = row[2:]
        # print(row, line_data_only)
        key = "-".join(row[1].split(" -- "))
        if key == "0" : 
            key = "0-idle"
        for cell_idx in range(len(line_data_only)) :
            column_cpu = header[cell_idx].split("/")[2]
            # print("==== ", column_cpu, core_type_dict)
            # print(column_cpu in core_type_dict, "(msec)" not in header[cell_idx], top_bin[cell_idx])
            if column_cpu in core_type_dict and "(msec)" not in header[cell_idx] and int(float(top_bin[cell_idx])) != 100: 
                core_name = core_type_dict[column_cpu]
                if core_name not in line_dict :
                    line_dict[core_name] = float(line_data_only[cell_idx])
                    line_dict[core_name+"_num"] = 1
                else :
                    line_dict[core_name] += float(line_data_only[cell_idx])
                    line_dict[core_name+"_num"] += 1
        # print("line_dict: ", line_dict)
        sum_list = ["-"] * len(data[header_start])
        for core_idx in range(len(data[header_start])) :    
            core_name = data[header_start][core_idx]
            if core_name in line_dict:
                sum_list[core_idx] = round(line_dict[core_name] / line_dict[core_name+"_num"], 2)
        data[key] = sum_list.copy()
        # print(key, data[key])
        # print(line_data_only)
    table['table_data'] = data

def coreFreqAvrTable(table, keyIdx, ValueIdx):
    copied = table['table_data'].copy()
    data = {copied[0][keyIdx]:copied[0][ValueIdx]}
    for index in range(1, len(copied), 1):
        key = copied[index][keyIdx].split("/")[2]
        value = copied[index][ValueIdx]
        data[key] = value
    table['table_data'] = data

def coreResidencyTable(table) :
    copied = table['table_data'].copy()
    data = {copied[0][0]:copied[1][0]}
    for index in range(1, len(copied[0]), 1):
        key = copied[0][index].split("/")[-1]
        if key.rfind("(%)") < 0:
            break
        value = copied[1][index]
        data[key] = value
    table['table_data'] = data

def osWakeupsTable(table) :
    copied = table['table_data'].copy()
    data = dict()
    for idx in range(len(copied)):
        line = copied[idx]
        key = line[0]
        if idx == 0:
            key = "OS_wakeups"
            value = line[1].split(" ")[0]+" ("+" ".join(line[2].split(" ")[:-1])+")"
        elif idx == 1:
            key = "Rank"
            value = line[1].split(" ")[0]+" ("+line[2]+")"
        else :
            value = line[1].split(" ")[0]+" ("+line[2]+")"
        data[key] = value
    table['table_data'] = data

def defaultResidencyTable(table, keyIdx, ValueIdx) :
    copied = table['table_data'].copy()
    data = dict()
    for idx in range(len(copied)):
        line = copied[idx]
        key = line[keyIdx]
        if "_Pstate" in table['label'] and idx > 0:
            key = key.split(".")[0]
        data[key] = line[ValueIdx]
    table['table_data'] = data


def socwatchTableTypeChecker(table, core_type) :

    label = table['label']
    if label == 'CPU_model':
        cpuModelTable(table)
    elif label == 'Core_Cstate' or label == 'ACPI_Cstate' : 
        coreResidencyTable(table)
    elif label == 'OS_wakeups':
        osWakeupsTable(table)
    elif label == 'CPU_Pavr' : 
        coreFreqAvrTable(table, 0, 1)
    elif label == 'CPU_Pstate' : 
        coreFreqResidencyTable(table, core_type)
    elif label == 'DC_count':
        oneLineColonSeperater(table)
    elif label == 'DDR_BW' or label == 'IO_BW' or label == 'VC1_BW' or label == 'NPU_BW' or label == 'Media_BW' or label == 'IPU_BW' or label == 'CCE_BW' or label == 'GT_BW' or label == 'D2D_BW':
        bwTotalAvr(table)
    elif label == "CPU_temp" or label == "SoC_temp":
        tempAvrTable(table)
    else :
        defaultResidencyTable(table, 0, 1)

def extractHeader(table) :

    if table["label"] not in socwatch_header_dict:
        socwatch_header_dict[table["label"]] = [key for key in table['table_data']]
    else :
        prev_keys = socwatch_header_dict[table["label"]]
        new_keys = [key for key in table['table_data']]
        set_keys = prev_keys.copy()
        for item in new_keys :
            if item not in prev_keys :
                set_keys.append(item)
        socwatch_header_dict[table["label"]] = set_keys


def parseSocwatch(abs_path, socwatch_targets) :

    socwatch_obj = dict()
    socwatch_obj['socwatch_path'] = abs_path
    socwatch_obj['socwatch_tables'] = []
    socwatch_obj['core_number'] = 0
    CORE_TYPE = None
    with open(abs_path, 'r') as file:

        for target in socwatch_targets : 
            tTable = dict()
            for line in file :
                tline = line.strip()
                if 'isCompleted' in tTable and tTable['isCompleted'] == False :

                    # if the table_data is initiated, 'isCompleted' exists, keep collecting line until empty line comes
                    if tline == "" :
                        tTable['isCompleted'] = True
                        socwatchTableTypeChecker(tTable, CORE_TYPE)
                        extractHeader(tTable)
                        socwatch_obj['socwatch_tables'].append(tTable)

                        # need to re-write this portion
                        if tTable['label'] == 'CPU_model':
                            CORE_TYPE = tTable['table_data'].copy()
                        break
                    else :
                        line_list = [item.strip() for item in tline.split(',')]
                        # print("======", tline, line_list)
                        line_list_num = len(line_list)
                        # this is removing '--------------' seperating line
                        # len(set(line_list[line_list_num-1])) returns number of different char, '-----' return 1, only contains single char
                        if line_list_num > 0 and len(set(line_list[line_list_num-1])) != 1 :
                            tTable['table_data'].append(line_list)
                elif tline.rfind(target['lookup']) >=0 :
                    tTable['label'] = target['key']
                    tTable['table_data'] = list()
                    tTable['isCompleted'] = False  

        return socwatch_obj

# def getBuckets(key) :
#     for item in socwatch_targets :
#         if key == item["key"] and "buckets" in item :
#             return item['buckets']
#     return None
        
def pStateBecketizer(header_dict, socwatch_targets) :

    for item in socwatch_targets : 
        if "buckets" in item :
            key = item["key"]
            new_list = list()
            new_list.append(header_dict[key][0])
            new_list.extend(item["buckets"])
            header_dict[key] = new_list

    # print("===", header_dict)





def getSocwatchHeader(socwatch_targets) :
    pStateBecketizer(socwatch_header_dict, socwatch_targets)
    return socwatch_header_dict
