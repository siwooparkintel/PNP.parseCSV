
import os
from os import listdir
from os.path import isfile, join
import tools
import model_output_parser as mop
import socwatch_summary_parser as soc
import power_summary_parser as psp
import power_checker as pck
import reporter as rpt



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

#BASE = os.getcwd()
BASE = "\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\full_data"

#result_list_csv = f"{BA}\\file_list.csv"
parsed_csv = f"{BASE}\\AI_models_parsed_results.csv"

hobl_sets = list()



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
    # if MODEL_OUTPUT not in dataset["data_type"] :
    #     dataset["data_type"].append(MODEL_OUTPUT)
    #dataset["model_output_path"] = abs_path
    dataset["model_output_obj"] = mop.parseModelResults(abs_path, AI_parsing_items)

def add_power(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    if POWER not in dataset["data_type"] :
        dataset["data_type"].append(POWER)
    dataset["power_data"] = psp.parsePowerSummaryCSV(abs_path, DAQ_target)

def add_socwatch(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    if SOCWATCH not in dataset["data_type"] :
        dataset["data_type"].append(SOCWATCH)
    dataset["socwatch_data"] = soc.parseSocwatch(abs_path)




def fileClassifier(abs_path, f):

    file_type = CL_UNCLASSIFIED
    
    if f == CL_PASS :
        createDataset(tools.splitLastItem(abs_path, "\\", 1)[0])
    elif f.find(CL_ETL) >= 0 and f.find(CL_SOCWATCH) == -1 : 
        # print("ETL detected ", abs_path, f)
        add_etl(abs_path)
        file_type = CL_ETL
    # elif f.find(CL_OUTPUT) >= 0 and f.find(CL_AI_MODEL) >= 0 :
    elif f.find(CL_OUTPUT) >= 0 :
        # print("AI_model output detected ", abs_path, f)
        add_model_output(abs_path)
        file_type = CL_OUTPUT
    elif f.find(CL_DAQ_SUMMARY) >= 0:
        #print("DAQ power summary detected ", abs_path, f)
        add_power(abs_path)
        file_type = CL_DAQ_SUMMARY
    elif f.find(CL_SOCWATCH) >= 0:
        #workload_name = "_".join(f.split("_")[:-1])
        #upto_path = ("\\").join(abs_path.split("\\")[:-1])
        workload_name = tools.splitLastItem(f, "_", 1)[0]
        upto_path = tools.splitLastItem(abs_path, "\\", 1)[0]
        soc_summary = workload_name + ".csv"
        summary_fullPath = os.path.join(upto_path, soc_summary)
        if os.path.exists(summary_fullPath) :
            # print("Socwatch ETL detected : ", f, " ::: detected summary : ", summary_fullPath)
            add_socwatch(summary_fullPath)
        else :
            print("=========================== No summary, Socwatch post-process may have interrupted")
        file_type = CL_SOCWATCH
    return file_type

"""
    elif f.find(CL_OUTPUT) >= 0 and f.find(CL_AI_MODEL) >= 0 and f.find("NPU") >= 0:
        print("AI_model NPU output detected ", abs_path, f)
        file_type = CL_OUTPUT
"""

def detectAndParseFile(path) :

    for f in os.listdir(path):
        abs_path = os.path.join(path, f)
        # print("================", abs_path)

        # if f == "Model_PSA_v6_4_a_qdq_proxy":
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
    pck.checkAndMarkPower(hobl_sets)
    # print("====[hobl_sets]", hobl_sets)
    

    rpt.writeParsedInCSV(parsed_csv, hobl_sets, AI_parsing_items)


main()




# =======================================================
# example of the parsed model output result data structure
# =======================================================
'''
{
'ID_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_000',
'data_label': 'Model_A3_v1_2_3_qdq_proxy_stripped',
'data_type': ['POWER', 'ETL'], 
'power_data': {'V_VAL_VCC_PCORE': 0.930583, 'I_VAL_VCC_PCORE': 4.14682, 'V_VAL_VCC_ECORE': 0.426789, 'I_VAL_VCC_ECORE': 0.661671, 'V_VAL_VCCSA': 0.828573, 'I_VAL_VCCSA': 0.692554, 'V_VAL_VCCGT': 0.694191, 'I_VAL_VCCGT': 4.886309, 'P_VCC_PCORE': 5.298088, 'P_VCC_ECORE': 0.601947, 'P_VCCSA': 0.630201, 'P_VCCGT': 4.426103, 'P_VCCL2': 0.016427, 'P_VCC1P8': 0.061738, 'P_VCCIO': 0.209027, 'P_VCCDDRIO': 0.060283, 'P_VNNAON': 0.115388, 'P_VNNAONLV': 0.01005, 'P_VDDQ': 0.02288, 'P_VDD2H': 0.452025, 'P_VDD2L': 0.020797, 'P_V1P8U_MEM': 0.033313, 'P_SOC+MEMORY': 11.959465, 'Run Time': 26.2, 'file_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_000\\AI_GPU_model_stripped_000\\AI_GPU_model_stripped_000_pacs-summary.csv', 'power_type': 'ETL_POWER', 'picked': 'picked'},
'etl_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_000\\AI_GPU_model_stripped_000.etl',
'model_output_obj': {'model_output_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_000\\GPU_Model_A3_v1_2_3_qdq_proxy_stripped_output.txt', 'model_output_data': {'read_model': [22.14, 'ms'], 'compile_model': [282.19, 'ms'], 'start_mem_usage': [None, ''], 'end_mem_usage': [None, ''], 'ram_used': [None, ''], 'first_inference': [1.65, 'ms'], 'device': ['GPU.', ''], 'iterations': [44524.0, ''], 'duration': [20012.68, 'ms'], 'latency_median': [0.43, 'ms'], 'throughput': [2224.79, 'FPS']}, 'model_output_status': 'successful'}
},

{
'ID_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_001',
'data_label': 'Model_A3_v1_2_3_qdq_proxy_stripped',
'data_type': ['POWER'], 
'power_data': {'V_VAL_VCC_PCORE': 0.974846, 'I_VAL_VCC_PCORE': 4.451328, 'V_VAL_VCC_ECORE': 0.393696, 'I_VAL_VCC_ECORE': 0.560568, 'V_VAL_VCCSA': 0.802704, 'I_VAL_VCCSA': 0.61567, 'V_VAL_VCCGT': 0.72095, 'I_VAL_VCCGT': 5.220127, 'P_VCC_PCORE': 5.713308, 'P_VCC_ECORE': 0.502492, 'P_VCCSA': 0.534047, 'P_VCCGT': 4.730054, 'P_VCCL2': 0.01456, 'P_VCC1P8': 0.061015, 'P_VCCIO': 0.115397, 'P_VCCDDRIO': 0.049966, 'P_VNNAON': 0.077361, 'P_VNNAONLV': 0.00759, 'P_VDDQ': 0.019183, 'P_VDD2H': 0.401964, 'P_VDD2L': 0.022827, 'P_V1P8U_MEM': 0.028216, 'P_SOC+MEMORY': 12.279085, 'Run Time': 25.2, 'file_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_001\\AI_GPU_model_stripped_001\\AI_GPU_model_stripped_001_pacs-summary.csv', 'power_type': 'POWER'},
'model_output_obj': {'model_output_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_001\\GPU_Model_A3_v1_2_3_qdq_proxy_stripped_output.txt', 'model_output_data': {'read_model': [8.38, 'ms'], 'compile_model': [228.12, 'ms'], 'start_mem_usage': [None, ''], 'end_mem_usage': [None, ''], 'ram_used': [None, ''], 'first_inference': [1.45, 'ms'], 'device': ['GPU.', ''], 'iterations': [47521.0, ''], 'duration': [20000.8, 'ms'], 'latency_median': [0.39, 'ms'], 'throughput': [2375.96, 'FPS']}, 'model_output_status': 'successful'}
},

{
'ID_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_004',
'data_label': 'Model_A3_v1_2_3_qdq_proxy_stripped',
'data_type': ['POWER', 'SOCWATCH'],
'power_data': {'V_VAL_VCC_PCORE': 1.092376, 'I_VAL_VCC_PCORE': 6.75938, 'V_VAL_VCC_ECORE': 0.402821, 'I_VAL_VCC_ECORE': 0.115688, 'V_VAL_VCCSA': 0.759344, 'I_VAL_VCCSA': 0.525504, 'V_VAL_VCCGT': 0.704935, 'I_VAL_VCCGT': 4.958847, 'P_VCC_PCORE': 8.579051, 'P_VCC_ECORE': 0.086437, 'P_VCCSA': 0.418763, 'P_VCCGT': 4.493119, 'P_VCCL2': 0.002966, 'P_VCC1P8': 0.071756, 'P_VCCIO': 0.411603, 'P_VCCDDRIO': 0.039072, 'P_VNNAON': 0.202622, 'P_VNNAONLV': 0.015292, 'P_VDDQ': 0.013748, 'P_VDD2H': 0.341798, 'P_VDD2L': 0.031004, 'P_V1P8U_MEM': 0.027867, 'P_SOC+MEMORY': 14.737569, 'Run Time': 25.8, 'file_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_004\\AI_GPU_model_stripped_004\\AI_GPU_model_stripped_004_pacs-summary.csv', 'power_type': 'SOCWATCH_POWER', 'picked': 'picked'},
'model_output_obj': {'model_output_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_004\\GPU_Model_A3_v1_2_3_qdq_proxy_stripped_output.txt', 'model_output_data': {'read_model': [8.36, 'ms'], 'compile_model': [229.75, 'ms'], 'start_mem_usage': [None, ''], 'end_mem_usage': [None, ''], 'ram_used': [None, ''], 'first_inference': [1.79, 'ms'], 'device': ['GPU.', ''], 'iterations': [45097.0, ''], 'duration': [20007.72, 'ms'], 'latency_median': [0.41, 'ms'], 'throughput': [2253.98, 'FPS']}, 'model_output_status': 'successful'},
'socwatch_data': '=========== hi ! in socwatch_summary_parser.py \\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\mixedTest\\GPU\\Model_A3_v1_2_3_qdq_proxy_stripped\\AI_GPU_model_stripped_004\\socwatch\\AI_GPU_model_stripped.csv'},




# model_parsed data structure
{'model_output_obj': {
    'model_output_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\GPU\\Model_A3_1_2_0_qdq_proxy_stripped\\AI_GPU_model_stripped_000\\GPU_Model_A3_1_2_0_qdq_proxy_stripped_output.txt',
    'model_output_data': {
        'read_model': [16.09, 'ms'],
        'compile_model': [2904.89, 'ms'],
        'first_inference': [1.45, 'ms'],
        'latency_median': [0.41, 'ms'],
        'throughput': [2311.1, 'FPS']
        },
    'model_output_status': 'successful'
    }
}
'''