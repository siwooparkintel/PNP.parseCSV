
import os
import time
from os import listdir
from os.path import isfile, join
import parsers.tools as tools
import parsers.model_output_parser as mop
import parsers.socwatch_summary_parser as soc
import parsers.power_summary_parser as psp
import parsers.power_checker as pck
import parsers.reporter as rpt


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
    {"key": "NPU_Pstate", "lookup": "Neural Processing Unit (NPU) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "1900", "1901-2900", "2901-3899", "3900"]},
    {"key": "MEMSS_Pstate", "lookup": "Memory Subsystem (MEMSS) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "NoC_Pstate", "lookup": "Network on Chip (NoC) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["400", "401-1049", "1050"]},
    {"key": "iGFX_Pstate", "lookup": "Integrated Graphics P-State/Frequency Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "400", "401-1799", "1800-2049", "2050"]}
]


AI_parsing_items = [
    {"key": "read_model", "lookup": "[ INFO ] Read model took", "unit":"ms"},
    {"key": "compile_model", "lookup": "[ INFO ] Compile model took", "unit":"ms"},
    {"key": "start_mem_usage", "lookup": "[ INFO ] Start of compilation memory usage: Peak", "unit":"KB"},
    {"key": "end_mem_usage", "lookup": "[ INFO ] End of compilation memory usage: Peak", "unit":"KB"},
    {"key": "ram_used", "lookup": "[ INFO ] Compile model ram used", "unit":"KB"},
    {"key": "first_inference", "lookup": "[ INFO ] First inference took", "unit":"ms"},
    {"key": "device", "lookup": "[ INFO ] Execution Devices:", "unit":""},
    {"key": "iterations", "lookup": "[ INFO ] Count:", "unit":""},
    {"key": "duration", "lookup": "[ INFO ] Duration:", "unit":"ms"},   
    {"key": "latency_median", "lookup": "[ INFO ]    Median:", "unit":"ms"},
    {"key": "throughput", "lookup": "[ INFO ] Throughput:", "unit":"FPS"}
]

DAQ_target = {
"V_VAL_VCC_PCORE":0,
"I_VAL_VCC_PCORE":0,
"V_VAL_VCC_ECORE":0,
"I_VAL_VCC_ECORE":0,
"V_VAL_VCCSA":0,
"I_VAL_VCCSA":0,
"V_VAL_VCCGT":0,
"I_VAL_VCCGT":0,
"P_VCC_PCORE":0,
"P_VCC_ECORE":0,
"P_VCCSA":0,
"P_VCCGT":0,
"P_VCCL2":0,
"P_VCC1P8":0,
"P_VCCIO":0,
"P_VCCDDRIO":0,
"P_VNNAON":0,
"P_VNNAONLV":0,
"P_VDDQ":0,
"P_VDD2H":0,
"P_VDD2L":0,
"P_V1P8U_MEM":0,
"P_SOC+MEMORY":0,
"Run Time":0
}


CL_UNCLASSIFIED = "unclassified"
CL_ETL = ".etl"
CL_OUTPUT = '_output.txt'
CL_SOCWATCH = 'Session.etl'
CL_AI_MODEL = '_qdq_proxy_'
CL_DAQ_SUMMARY = 'pacs-summary.csv'
CL_PASS = ".PASS"

ETL = "ETL"
POWER = "POWER"
SOCWATCH = "SOCWATCH"
MODEL_OUTPUT = "MODEL_OUTPUT"
MIN = "MIN"
MAX = "MAX"
MED = "MED"



#BASE = os.getcwd()
BASE = "\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data"

#result_list_csv = f"{BA}\\file_list.csv"
result_csv = f"{BASE}\\AI_models_parsed_results"

hobl_sets = list()

file_num = 0

'''
====================================================================================
To parse everything: 


To parse everything picked by power_pick (MIN, MAX, Median)


To parse only median picked power


To parse every POWER_SOCWATCH

====================================================================================
'''
# data_direction : 'vertical' or 'horizontal'

picks = {'only_picks':True, 'power_pick':MED, 'data_direction':'vertical'}






    
#=========================================================================
# this returns parent or parent*2 folder name string as a data_set name
# if ETL, Power, Socwatch folder separation structure,
# it returns grand parent folder name
#=========================================================================
def getDatasetLabel(abs_path) :
    folder_list = abs_path.split("\\")[:-1]
    last = folder_list[len(folder_list)-1]
    last_lower = last.lower()
    if last_lower == 'etl' or last_lower == 'power' or last_lower == 'socwatch':
        return folder_list[len(folder_list)-2]
    else :
        return last

def createDataset(abs_path) :
    hobl_sets.append({
        "ID_path":abs_path,
        "data_label":getDatasetLabel(abs_path),
        "data_type":[]
    })

def pullData(abs_path) :
    for item in hobl_sets:
        if (abs_path.find(item["ID_path"]) == 0) : 
            return item
    return None

def calFromPowerModel(block) :
    if 'power_obj' in block and 'model_output_obj' in block :
        if 'power_data' in block['power_obj'] and block['model_output_obj']['model_output_status'] != "failed" and 'model_output_data' in block['model_output_obj']:
            # calculate 'Eng(J)/Frame' here
            block['power_obj']['power_data']['Eng(J)/Frame'] = block['power_obj']['power_data']['Energy (J)'] / block['model_output_obj']['model_output_data']['throughput'][0]
        else :
            # tools.errorAndExit("===error in claFromPowerModel===" + str(block))
            block['power_obj']['power_data']['Eng(J)/Frame'] = "n/a"

def add_etl(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    if ETL not in dataset["data_type"] :
        dataset["data_type"].append(ETL)
    dataset["etl_path"] = abs_path

def add_model_output(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    dataset["model_output_obj"] = mop.parseModelResults(abs_path, AI_parsing_items)
    calFromPowerModel(dataset)
    global file_num
    file_num += 1

def add_power(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    if POWER not in dataset["data_type"] :
        dataset["data_type"].append(POWER)
    dataset["power_obj"] = psp.parsePowerSummaryCSV(abs_path, DAQ_target)
    calFromPowerModel(dataset)
    global file_num
    file_num += 1


def add_socwatch(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    if SOCWATCH not in dataset["data_type"] :
        dataset["data_type"].append(SOCWATCH)
    dataset["socwatch_obj"] = soc.parseSocwatch(abs_path, socwatch_targets)
    global file_num
    file_num += 1



def fileClassifier(abs_path, f):

    file_type = CL_UNCLASSIFIED
    
    if f == CL_PASS :
        createDataset(tools.splitLastItem(abs_path, "\\", 1)[0])
    elif f.find(CL_ETL) >= 0 and f.find(CL_SOCWATCH) == -1 : 
        # print("ETL detected ", abs_path, f)
        add_etl(abs_path)
        file_type = CL_ETL
    elif f.find(CL_OUTPUT) >= 0 :
        add_model_output(abs_path)
        file_type = CL_OUTPUT
    elif f.find(CL_DAQ_SUMMARY) >= 0:
        add_power(abs_path)
        file_type = CL_DAQ_SUMMARY
    elif f.find(CL_SOCWATCH) >= 0:
        workload_name = tools.splitLastItem(f, "_", 1)[0]
        upto_path = tools.splitLastItem(abs_path, "\\", 1)[0]
        soc_summary = workload_name + ".csv"
        summary_fullPath = os.path.join(upto_path, soc_summary)
        if os.path.exists(summary_fullPath) :
            add_socwatch(summary_fullPath)
        else :
            print("===== No Socwatch summary, Socwatch post-process may have interrupted", abs_path)
        file_type = CL_SOCWATCH
    return file_type


def detectAndParseFile(path) :

    for f in os.listdir(path):
        abs_path = os.path.join(path, f)
        # if f == "Model_A3_v1_2_3_qdq_proxy_stripped":
        #     break
        if os.path.isfile(abs_path):
            fType = fileClassifier(abs_path, f)
            if fType == CL_SOCWATCH :
                # after detecting first Socwatch ETL, and it's summary, no need to go further
                break
        else:
            #recursive on a folder detection
            detectAndParseFile(abs_path)

def main():

    detectAndParseFile(BASE)
    pck.checkAndMarkPower(hobl_sets, picks)
    # print("====[hobl_sets]", hobl_sets)
    rpt.writeParsedInCSV(result_csv, hobl_sets, socwatch_targets, picks)


start_time = time.perf_counter()
main()
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Parsing {file_num} files Successful! [Elapsed time:::] {elapsed_time} seconds")







# =======================================================
# example of the parsed model output result data structure
# =======================================================




# model_parsed data structure
"""
{'ID_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_003',
'data_label': 'Model_C2_v1_2_1_qdq_proxy',
'data_type': ['POWER'], 
'power_obj': {
    'power_data': {
        'V_VAL_VCC_PCORE': 0.81286,
        'I_VAL_VCC_PCORE': 1.008848,
        'V_VAL_VCC_ECORE': 0.197352, 'I_VAL_VCC_ECORE': 0.030435, 'V_VAL_VCCSA': 1.103559, 'I_VAL_VCCSA': 5.676103, 'V_VAL_VCCGT': 0.000814, 'I_VAL_VCCGT': 5.9e-05, 'P_VCC_PCORE': 0.983881, 'P_VCC_ECORE': 0.016794, 'P_VCCSA': 6.850881, 'P_VCCGT': 0.000116, 'P_VCCL2': 0.000939, 'P_VCC1P8': 0.067862, 'P_VCCIO': 0.179597, 'P_VCCDDRIO': 0.15445, 'P_VNNAON': 0.10042, 'P_VNNAONLV': 0.007033, 'P_VDDQ': 0.078012, 'P_VDD2H': 1.026172, 'P_VDD2L': 0.002483, 'P_V1P8U_MEM': 0.060241,
        'P_SOC+MEMORY': 9.535497, 
        'Run Time': 25.6, 
        'Energy (J)': 244.1087232, 
        'Eng(J)/Frame': 0.1339372767974717},
    'file_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_003\\AI_NPU_model_stripped_003\\AI_NPU_model_stripped_003_pacs-summary.csv',
    'power_type': 'POWER',
    'picked': 'picked'},
'model_output_obj': {
    'model_output_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_003\\NPU_Model_C2_v1_2_1_qdq_proxy_output.txt',
    'model_output_data': {
        'read_model': [26.19, 'ms'],
        'compile_model': [35.88, 'ms'],
        'start_mem_usage': [126644.0, 'KB'],
        'end_mem_usage': [145424.0, 'KB'], 
        'ram_used': [18780.0, 'KB'], 
        'first_inference': [4.13, 'ms'], 
        'device': ['NPU', ''], 
        'iterations': [36452.0, ''], 
        'duration': [20000.45, 'ms'], 
        'latency_median': [0.54, 'ms'], 
        'throughput': [1822.56, 'FPS']},
    'model_output_status': 'successful'}
},

{'ID_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004', 'data_label': 'Model_C2_v1_2_1_qdq_proxy', 
'data_type': ['POWER', 'SOCWATCH'],
'power_obj': {
    'power_data': {
        'V_VAL_VCC_PCORE': 0.747903, 'I_VAL_VCC_PCORE': 0.991634, 
        'V_VAL_VCC_ECORE': 0.279867, 'I_VAL_VCC_ECORE': 0.039626, 
        'V_VAL_VCCSA': 1.104632, 'I_VAL_VCCSA': 5.497834, 
        'V_VAL_VCCGT': 0.000573, 'I_VAL_VCCGT': -0.000137, 
        'P_VCC_PCORE': 0.936324, 
        'P_VCC_ECORE': 0.02296, 
        'P_VCCSA': 6.644626, 
        'P_VCCGT': 3.4e-05, 
        'P_VCCL2': 0.001612, 
        'P_VCC1P8': 0.069989, 
        'P_VCCIO': 0.396728, 
        'P_VCCDDRIO': 0.152057, 
        'P_VNNAON': 0.193041, 
        'P_VNNAONLV': 0.013124, 
        'P_VDDQ': 0.076898, 
        'P_VDD2H': 1.004154, 
        'P_VDD2L': 0.002397, 
        'P_V1P8U_MEM': 0.059089, 
        'P_SOC+MEMORY': 9.579855, 
        'Run Time': 25.4, 
        'Energy (J)': 243.328317, 
        'Eng(J)/Frame': 0.13881709253966354}, 
    'file_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004\\AI_NPU_model_stripped_004\\AI_NPU_model_stripped_004_pacs-summary.csv',
    'power_type': 'POWER_SOCWATCH', 
    'picked': 'picked'},
'model_output_obj': {
    'model_output_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004\\NPU_Model_C2_v1_2_1_qdq_proxy_output.txt',
    'model_output_data': {
        'read_model': [26.19, 'ms'], 
        'compile_model': [44.46, 'ms'], 
        'start_mem_usage': [126708.0, 'KB'], 
        'end_mem_usage': [145232.0, 'KB'], 
        'ram_used': [18524.0, 'KB'], 
        'first_inference': [9.73, 'ms'], 
        'device': ['NPU', ''], 
        'iterations': [35058.0, ''], 
        'duration': [20000.36, 'ms'], 
        'latency_median': [0.56, 'ms'], 
        'throughput': [1752.87, 'FPS']
    }, 
    'model_output_status': 'successful'}, 
'socwatch_obj': {
    'socwatch_path': '\\\\255.255.255.255\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004\\socwatch\\AI_NPU_model_stripped.csv',
    'socwatch_tables': [
        {'label': 'pkg_cstate', 
         'table_data': [
            ['C-State', 'Package Residency (%)', 'Package Residency (msec)'], 
            ['PC0', '68.54', '23559.76'], 
            ['PC2', '1.79', '615.24'], 
            ['PC6.1', '0.00', '0.00'], 
            ['PC6.2', '0.21', '72.28'], 
            ['PC10.1', '0.15', '53.21'], 
            ['PC10.2', '29.31', '10075.41'], 
            ['PC10.3', '0.00', '0.00']], 
        'isOpen': False
        },{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
}}]

"""