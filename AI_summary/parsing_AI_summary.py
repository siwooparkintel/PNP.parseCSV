
import os
import time
from os import listdir
from os.path import isfile, join
import parsers.tools as tools
import parsers.model_output_parser as mop
import parsers.socwatch_summary_parser as soc
import parsers.power_summary_parser as psp
import parsers.power_trace_parser as ptp
import parsers.power_checker as pck
import parsers.reporter as rpt

import argparse

parser = argparse.ArgumentParser(prog='AI summary parser')
parser.add_argument('-i', '--input', help='input path. this will be the bese of the summray, will detect all files and folders from that path tree')
parser.add_argument('-o', '--output', help='output path. location of file and file name')
# parser.print_help()
args = parser.parse_args()
print("args: ", args)

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
"V_VAL_VCC_PCORE":-1,
"I_VAL_VCC_PCORE":-1,
"V_VAL_VCC_ECORE":-1,
"I_VAL_VCC_ECORE":-1,
"V_VAL_VCCSA":-1,
"I_VAL_VCCSA":-1,
"V_VAL_VCCGT":-1,
"I_VAL_VCCGT":-1,
"P_VCC_PCORE":-1,
"P_VCC_ECORE":-1,
"P_VCCSA":-1,
"P_VCCGT":-1,
"P_VCCL2":-1,
"P_VCC1P8":-1,
"P_VCCIO":-1,
"P_VCCDDRIO":-1,
"P_VNNAON":-1,
"P_VNNAONLV":-1,
"P_VDDQ":-1,
"P_VDD2H":-1,
"P_VDD2L":-1,
"P_V1P8U_MEM":-1,
"P_SOC+MEMORY":-1,
"Run Time":-1
}


CL_UNCLASSIFIED = "unclassified"
CL_ETL = ".etl"
CL_OUTPUT = '_output.txt'
CL_SOCWATCH = 'Session.etl'
CL_AI_MODEL = '_qdq_proxy_'
CL_DAQ_SUMMARY = 'pacs-summary.csv'
CL_DAQ_TRACES = 'pacs-traces'
CL_PASS = ".PASS"

ETL = "ETL"
POWER = "POWER"
SOCWATCH = "SOCWATCH"
MODEL_OUTPUT = "MODEL_OUTPUT"
MIN = "MIN"
MAX = "MAX"
MED = "MED"



#BASE = os.getcwd()
# BASE = "\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data"
BASE = args.input
result_csv = args.output



if result_csv == None : 
    result_csv = f"{BASE}\\AI_models_summary"




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

picks = {'only_picks':True, 'power_pick':MED, 'data_direction':'vertical', 'inferencing_power':True}






    
#=========================================================================
# this returns parent or parent*2 folder name string as a data_set name
# if ETL, Power, Socwatch folder separation structure,
# it returns grand parent folder name
#=========================================================================
def getDatasetLabel(abs_path) :
    folder_list = abs_path.split("\\")[:-1]
    last = folder_list[-1]
    last_lower = last.lower()
    if last_lower == 'etl' or last_lower == 'power' or last_lower == 'socwatch':
        return [folder_list[-3], folder_list[-2]]
    else :
        return [folder_list[-2], folder_list[-1]]

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

def add_trace(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    dataset["trace_obj"] = ptp.parsePowerTraceCSV(abs_path)
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
    elif f.find(CL_DAQ_TRACES) >= 0 and f.find('sr.csv') >= 0:
        add_trace(abs_path)
        file_type = CL_DAQ_TRACES
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
    if (picks["inferencing_power"] == True) : 
        ptp.averageInferencingPower(hobl_sets, DAQ_target)
    # ===========================================================================
    # print processed(fully parsed) data to check the dictionary (Object) structure
    # since it is keep improving, changing
    # ===========================================================================
    print("====[hobl_sets]", hobl_sets)
    # rpt.writeParsedInCSV(result_csv, hobl_sets, socwatch_targets, picks)


start_time = time.perf_counter()
main()
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Parsing {file_num} files Successful! [Elapsed time:::] {elapsed_time} seconds")







# ===========================================================================
# print processed(fully parsed) data above in the main() to check the dictionary (Object) structure
# since it is keep improving, changing. 
# ===========================================================================


"""
{
    'ID_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004',
    'data_label': ['NPU', 'Model_C2_v1_2_1_qdq_proxy'], 
    'data_type': ['POWER', 'SOCWATCH'], 
    'power_obj': {'power_data': {'V_VAL_VCC_PCORE': 0.747903, 'I_VAL_VCC_PCORE': 0.991634, 'V_VAL_VCC_ECORE': 0.279867, 'I_VAL_VCC_ECORE': 0.039626, 'V_VAL_VCCSA': 1.104632, 'I_VAL_VCCSA': 5.497834, 'V_VAL_VCCGT': 0.000573, 'I_VAL_VCCGT': -0.000137, 'P_VCC_PCORE': 0.936324, 'P_VCC_ECORE': 0.02296, 'P_VCCSA': 6.644626, 'P_VCCGT': 3.4e-05, 'P_VCCL2': 0.001612, 'P_VCC1P8': 0.069989, 'P_VCCIO': 0.396728, 'P_VCCDDRIO': 0.152057, 'P_VNNAON': 0.193041, 'P_VNNAONLV': 0.013124, 'P_VDDQ': 0.076898, 'P_VDD2H': 1.004154, 'P_VDD2L': 0.002397, 'P_V1P8U_MEM': 0.059089, 'P_SOC+MEMORY': 9.579855, 'Run Time': 25.4, 'Energy (J)': 243.328317, 'Eng(J)/Frame': 0.13881709253966354}, 'file_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004\\AI_NPU_model_stripped_004\\AI_NPU_model_stripped_004_pacs-summary.csv', 'power_type': 'POWER_SOCWATCH', 'picked': 'picked'}, 
    'model_output_obj': {'model_output_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004\\NPU_Model_C2_v1_2_1_qdq_proxy_output.txt', 'model_output_data': {'read_model': [26.19, 'ms'], 'compile_model': [44.46, 'ms'], 'start_mem_usage': [126708.0, 'KB'], 'end_mem_usage': [145232.0, 'KB'], 'ram_used': [18524.0, 'KB'], 'first_inference': [9.73, 'ms'], 'device': ['NPU', ''], 'iterations': [35058.0, ''], 'duration': [20000.36, 'ms'], 'latency_median': [0.56, 'ms'], 'throughput': [1752.87, 'FPS']}, 'model_output_status': 'successful'}, 
    'socwatch_obj': {
        'socwatch_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_004\\socwatch\\AI_NPU_model_stripped.csv', 'socwatch_tables': [
            {'label': 'CPU_model', 'table_data': {'Core_0 ': 'LNC', 'Core_1 ': 'LNC', 'Core_2 ': 'LNC', 'Core_3 ': 'LNC', 'Core_4 ': 'SKT', 'Core_5 ': 'SKT', 'Core_6 ': 'SKT', 'Core_7 ': 'SKT'}, 'isCompleted': True}, 
            {'label': 'PKG_Cstate', 'table_data': {'C-State': 'Package Residency (%)', 'PC0': '68.54', 'PC2': '1.79', 'PC6.1': '0.00', 'PC6.2': '0.21', 'PC10.1': '0.15', 'PC10.2': '29.31', 'PC10.3': '0.00'}, 'isCompleted': True}, 
            {'label': 'Core_Cstate', 'table_data': {'C-State': 'CC0', 'Core_0 Residency (%)': '9.84', 'Core_1 Residency (%)': '10.45', 'Core_2 Residency (%)': '3.97', 'Core_3 Residency (%)': '5.61', 'Core_4 Residency (%)': '0.27', 'Core_5 Residency (%)': '0.11', 'Core_6 Residency (%)': '0.07', 'Core_7 Residency (%)': '0.09'}, 'isCompleted': True}, 
            {'label': 'ACPI_Cstate', 'table_data': {'C-State': 'ACPI C0', 'Core_0 Residency (%)': '7.93', 'Core_1 Residency (%)': '8.62', 'Core_2 Residency (%)': '3.54', 'Core_3 Residency (%)': '4.66', 'Core_4 Residency (%)': '0.57', 'Core_5 Residency (%)': '0.14', 'Core_6 Residency (%)': '0.11', 'Core_7 Residency (%)': '0.11'}, 'isCompleted': True}, 
            {'label': 'OS_wakeups', 'table_data': {'OS_wakeups': 'Process (CPU %)', 'Rank': 'Overall (11.56)', '1': 'benchmark_app.exe (6.63)', '2': 'System (3.59)', '3': 'socwatch.exe (0.69)', '4': 'MsMpEng.exe (0.44)', '5': 'SimpleRemoteConsole.exe (0.24)'}, 'isCompleted': True}, 
            {'label': 'CPU_Pavr', 'table_data': {'CPU ID': 'Average (MHz)', 'Core_0': '1542', 'Core_1': '2015', 'Core_2': '1684', 'Core_3': '1324', 'Core_4': '1816', 'Core_5': '2450', 'Core_6': '2072', 'Core_7': '2081'}, 'isCompleted': True}, 
            {'label': 'CPU_Pstate', 'table_data': {
                'P-State': ['LNC', 'SKT'], 
                '5001-5100': [0.0, 0.0], 
                '4901-5000': [0.0, 0.0], 
                '4801-4900': [0.15, 0.0], 
                '4701-4800': [0.09, 0.0], '4601-4700': [0.0, 0.0], '4501-4600': [0.13, 0.0], '4401-4500': [0.16, 0.0], '4301-4400': [0.24, 0.0], '4201-4300': [0.0, 0.0], '4101-4200': [0.22, 0.0], '4001-4100': [0.06, 0.0], '3901-4000': [0.1, 0.0], '3801-3900': [0.28, 0.0], '3701-3800': [0.22, 0.0], '3601-3700': [0.16, 0.0], '3501-3600': [0.14, 0.0], '3401-3500': [0.04, 0.02], '3301-3400': [0.0, 0.05], '3201-3300': [0.38, 0.07], '3101-3200': [0.0, 0.0], '3001-3100': [0.01, 0.03], '2901-3000': [0.0, 0.01], '2801-2900': [0.26, 0.01], '2701-2800': [0.06, 0.0], '2601-2700': [0.21, 0.0], '2501-2600': [0.12, 0.0], '2401-2500': [0.39, 0.01], '2301-2400': [0.35, 0.01], '2201-2300': [0.98, 0.0], '2101-2200': [1.39, 0.03], '2001-2100': [0.32, 0.0], '1901-2000': [0.88, 0.05], '1801-1900': [0.59, 0.02], '1701-1800': [0.7, 0.01], '1601-1700': [1.96, 0.01], '1501-1600': [1.09, 0.01], '1401-1500': [2.09, 0.16], '1301-1400': [2.92, 0.01], '1201-1300': [5.29, 0.02], '1101-1200': [5.02, 0.04], '1001-1100': [1.86, 0.04], '901-1000': [0.22, 0.0], '801-900': [0.08, 0.0], '701-800': [0.08, 0.0], '601-700': [0.06, 0.0], '501-600': [0.02, 0.0], 
                '401-500': [0.0, 0.0], 
                '<= 400': [0.0, 0.0]}, 
            'isCompleted': True}, 
            {'label': 'RC_Cstate', 'table_data': {'C-State': 'iGPU/Graphics Residency (%)', 'RC0': '0.17', 'RC6': '99.83'}, 'isCompleted': True}, 
            {'label': 'DDR_BW', 'table_data': {'DDR_BW_AvrRt(MB/s)': '14650.70'}, 'isCompleted': True}, 
            {'label': 'IO_BW', 'table_data': {'IO_BW_AvrRt(MB/s)': '6.78'}, 'isCompleted': True}, 
            {'label': 'VC1_BW', 'table_data': {'VC1_BW_AvrRt(MB/s)': '2.05'}, 'isCompleted': True}, 
            {'label': 'NPU_BW', 'table_data': {'NPU_BW_AvrRt(MB/s)': '14660.05'}, 'isCompleted': True}, 
            {'label': 'Media_BW', 'table_data': {'Media_BW_AvrRt(MB/s)': '0.00'}, 'isCompleted': True}, 
            {'label': 'IPU_BW', 'table_data': {'IPU_BW_AvrRt(MB/s)': '0.00'}, 'isCompleted': True}, 
            {'label': 'CCE_BW', 'table_data': {'CCE_BW_AvrRt(MB/s)': '0.00'}, 'isCompleted': True}, 
            {'label': 'GT_BW', 'table_data': {'GT_BW_AvrRt(MB/s)': '0.25'}, 'isCompleted': True}, 
            {'label': 'D2D_BW', 'table_data': {'D2D_BW_AvrRt(MB/s)': '4.66'}, 'isCompleted': True}, 
            {'label': 'CPU_temp', 'table_data': {'CPU_temp': 'Time-weighted Avg (oC)', 'Core_0': '30.56', 'Core_1': '30.28', 'Core_2': '30.09', 'Core_3': '29.70', 'Core_4': '29.96', 'Core_5': '29.97', 'Core_6': '30.21', 'Core_7': '30.11'}, 'isCompleted': True}, 
            {'label': 'SoC_temp', 'table_data': {'SoC_temp': 'Time-weighted Avg (oC)', 'PCH': '30.03', 'SA': '32.18', 'IPU': '28.87', 'DE': '30.05', 'NPU': '32.05', 'MEDIA': '29.62'}, 'isCompleted': True}, 
            {'label': 'NPU_Dstate', 'table_data': {'State': 'Residency (%)', 'D0i3/D3': '41.00', 'D0 Active': '58.17', 'D0i2 Active': '0.00', 'D0i2 Idle': '0.83'}, 'isCompleted': True}, 
            {'label': 'DC_count', 'table_data': {'Up to DC5 or DC6 enabled (sampled count)': '293', 'Up to DC5 enabled (sampled count)': '0', 'Up to DC6 (including DC5) enabled (sampled count)': '293', 'DCx Clock-Off(DCxCO) state allowed by software': 'Do not allow'}, 'isCompleted': True}, 
            {'label': 'Media_Cstate', 'table_data': {'C-State': 'Residency (%)', 'Media-C0': '7.17', 'Media C6': '92.83'}, 'isCompleted': True}, 
            {'label': 'NPU_Pstate', 'table_data': {'Frequency (MHz)': 'NPU (%)', '0': '41.97', '1950': '0.48', '2450': '0.28', '2950': '0.32', '3500': '0.32', '3900': '56.63'}, 'isCompleted': True}, 
            {'label': 'MEMSS_Pstate', 'table_data': {'Frequency (MHz)': 'MEMSS (%)', '594': '42.49', '1584': '0.69', '2112': '56.82'}, 'isCompleted': True}, 
            {'label': 'NoC_Pstate', 'table_data': {'Frequency (MHz)': 'NOC (%)', '400': '41.97', '650': '1.08', '1050': '56.96'}, 'isCompleted': True}, 
            {'label': 'iGFX_Pstate', 'table_data': {'Frequency (MHz)': 'IGFX (%)', '0': '99.79', '400': '0.21'}, 'isCompleted': True}
        ], 
    'core_number': 8}}, 

            """