
"""
Socwatch Options:
Command line options: -s 0 -o c:\hobl_data\socwatch\AI_GPU_model_stripped -f temp -f npu -f gfx -f memss-pstate -f cpu-cstate -f hw-cpu-hwp -f hw-cpu-cstate -f hw-cpu-pstate -f os-cpu-cstate -f os-cpu-pstate -f hw-igfx-cstate -f hw-igfx-pstate -f display-state -f ddr-bw -f bw-all -f noc-pstate -f media-pstate -m -r auto --no-post-processing 
"""

socwatch_targets = [
    {"key": "CPU_model", "lookup": "CPU native model"},
    {"key": "PKG_Cstate", "lookup": "Platform Monitoring Technology CPU Package C-States Residency Summary: Residency (Percentage and Time)"},
    {"key": "Core_Cstate", "lookup": "Core C-State Summary: Residency (Percentage and Time)"},
    {"key": "ACPI_Cstate", "lookup": "Core C-State (OS) Summary: Residency (Percentage and Time)"},
    {"key": "OS_wakeups", "lookup": "Processes by Platform Busy Duration"},
    {"key": "CPU_Pavr", "lookup": "CPU P-State Average Frequency (excluding CPU idle time)"},
    {"key": "CPU_Pstate", "lookup": "CPU P-State/Frequency Summary: Residency (Percentage and Time)"},
    {"key": "RC_Cstate", "lookup": "Integrated Graphics C-State  Summary: Residency (Percentage and Time)"},
    {"key": "DDR_BW", "lookup": "DDR Bandwidth Requests by Component Summary: Average Rate and Total"},
    {"key": "IO_BW", "lookup": "IO Bandwidth Summary: Average Rate and Total"},
    {"key": "VC1_BW", "lookup": "Display VC1 Bandwidth Summary: Average Rate and Total"},
    {"key": "NPU_BW", "lookup": "Neural Processing Unit (NPU) to Memory Bandwidth Summary: Average Rate and Total"},
    {"key": "Media_BW", "lookup": "Media to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "IPU_BW", "lookup": "Image Processing Unit (IPU) to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "CCE_BW", "lookup": "CCE to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "GT_BW", "lookup": "Network on a Chip GT Bandwidth Summary: Average Rate and Total"},
    {"key": "D2D_BW", "lookup": "Network on a Chip Die to Die Bandwidth Summary: Average Rate and Total"},
    {"key": "CPU_temp", "lookup": "Temperature Metrics Summary - Sampled: Min/Max/Avg"},
    {"key": "SoC_temp", "lookup": "SoC Domain Temperatures Summary - Sampled: Min/Max/Avg"},
    {"key": "NPU_Dstate", "lookup": "Neural Processing Unit (NPU) D-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "DC_count", "lookup": "Dynamic Display State Enabling"},
    {"key": "Media_Cstate", "lookup": "Media C-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "NPU_Pstate", "lookup": "Neural Processing Unit (NPU) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "MEMSS_Pstate", "lookup": "Memory Subsystem (MEMSS) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "NoC_Pstate", "lookup": "Network on Chip (NoC) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "iGFX_Pstate", "lookup": "Integrated Graphics P-State/Frequency Summary - Sampled: Approximated Residency (Percentage)"}
]

socwatch_header_dict = dict()

def cpuModelTable(table) :
    copied = table['table_data'].copy()
    data = dict()
    for line in copied:
        items = line[0].split("=")
        if len(items) > 1 :
            key = items[0].split("/")[1]
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

def coreFreqResidencyTable(table):
    copied = table['table_data'].copy()
    data = {copied[0][0]:['LNC','SKT']}
    for index in range(1, len(copied)-1, 1) :
        row = copied[index]
        # print("==================", row)
        try :
            # print(row[1], (float(row[2])+float(row[3])+float(row[4])+float(row[5]))/4, (float(row[6])+float(row[7])+float(row[8])+float(row[9]))/4)
            key = "-".join(row[1].split(" -- "))
            pcore = (float(row[2])+float(row[3])+float(row[4])+float(row[5]))/4
            ecore = (float(row[6])+float(row[7])+float(row[8])+float(row[9]))/4
            data[key] = [round(pcore, 3), round(ecore, 3)]
        except :
            print("=== error in coreFreqResidencyTable ===", table)
            data[key] = None
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

def socwatchTableTypeChecker(table) :
    label = table['label']
    if label == 'Core_Cstate' or label == 'ACPI_Cstate' : 
        coreResidencyTable(table)
    elif label == 'OS_wakeups':
        osWakeupsTable(table)
    elif label == 'CPU_Pavr' : 
        coreFreqAvrTable(table, 0, 1)
    elif label == 'CPU_Pstate' : 
        coreFreqResidencyTable(table)
    elif label == 'CPU_model':
        cpuModelTable(table)
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


def parseSocwatch(abs_path) :

    socwatch_obj = dict()
    socwatch_obj['socwatch_path'] = abs_path
    socwatch_obj['socwatch_tables'] = []
    socwatch_obj['core_number'] = 0

    with open(abs_path, 'r') as file:

        for target in socwatch_targets : 
            tTable = dict()
            for line in file :
                tline = line.strip()
                if 'isCompleted' in tTable and tTable['isCompleted'] == False :

                    # if the table_data is initiated, 'isCompleted' exists, keep collecting line until empty line comes
                    if tline == "" :
                        tTable['isCompleted'] = True
                        socwatchTableTypeChecker(tTable)
                        extractHeader(tTable)
                        socwatch_obj['socwatch_tables'].append(tTable)
                        # need to re-write this portion
                        if tTable['label'] == 'CPU_model':
                            socwatch_obj['core_number'] = len(tTable['table_data'])
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
    
def getSocwatchHeader() :
    # print("========== in getSocwatchHeader(): ", socwatch_header_dict)
    for key in socwatch_header_dict:
        # print(key)
        if "_Pstate" in key and "CPU_Pstate" not in key :
            copied = socwatch_header_dict[key].copy()[1:]
            new_list = list()
            new_list.append(socwatch_header_dict[key][0])
            new_list.extend(sorted(copied, key=int))
            socwatch_header_dict[key] = new_list
    # print("========== in getSocwatchHeader(): ", socwatch_header_dict)    
    return socwatch_header_dict
