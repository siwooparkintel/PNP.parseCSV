import os
import time
from os import listdir
from os.path import isfile, join
import parsers.tools as tools
import parsers.pcie_socwatch_summary_parser as psoc
import parsers.socwatch_summary_parser as soc
import parsers.power_summary_parser as psp
import parsers.reporter as rpt

import argparse

parser = argparse.ArgumentParser(prog='Socwatch summary parser')
parser.add_argument('-i', '--input', help='json input will be here')
parser.add_argument('-o', '--output', help='output path. location of file and file name')
# parser.print_help()
args = parser.parse_args()
# print("args: ", args)

# sw prograssion data list of dicts
SWP = [
    {
        "data_label":"CataV3+CCA+LCLT+UHX2",
        "power_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2529.3_CV3CCALCLTUHX2\web_cataV3_si_003_Ppick\web_cataV3_si_003\web_cataV3_si_003_pacs-summary.csv",
        "socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2529.3_CV3CCALCLTUHX2\web_cataV3_si_004_Spick\socwatch\web_cataV3_si.csv",
        "PCIe_socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2529.3_CV3CCALCLTUHX2\web_cataV3_si_007_PCIe\socwatch\web_cataV3_si.csv"
    }
]
    # {
    #     "data_label":"CataV3+IT+CCA+LCLT+UHX2",
    #     "power_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2527.1_CataV3_UHX2\Power_CataV3_UHX2_001_ppick\Power_CataV3_UHX2_001_pacs-summary.csv",
    #     "socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2527.1_CataV3_UHX2\Socwatch_Power_CataV3_UHX2_003_spick\CataV3_UHX2_003\CataV3_IT_CCA_LCLT_UHX2_003.csv",
    #     "PCIe_socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2527.1_CataV3_UHX2\PCIe_Power_CataV3_UHX2_000\CataV3_UHX2_PCIe\CataV3_IT_CCA_LCLT_UHX2_PCIeOnly.csv"
    # },
    # {
    #     "data_label":"CataV3+CCA+LCLT+UHX2",
    #     "power_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2529.3_CV3CCALCLTUHX2\web_cataV3_si_003_Ppick\web_cataV3_si_003\web_cataV3_si_003_pacs-summary.csv",
    #     "socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2529.3_CV3CCALCLTUHX2\web_cataV3_si_004_Spick\socwatch\web_cataV3_si.csv",
    #     "PCIe_socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2529.3_CV3CCALCLTUHX2\web_cataV3_si_007_PCIe\socwatch\web_cataV3_si.csv"
    # }

    

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
    {"key": "Media_Pstate", "lookup": "Media P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "NoC_Pstate", "lookup": "Network on Chip (NoC) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["400", "401-1049", "1050"]},
    {"key": "D2D_Pstate", "lookup": "Die-to-die (D2D) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "Ring_Pstate", "lookup": "Ring P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "iGFX_Pstate", "lookup": "Integrated Graphics P-State/Frequency Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "400", "401-1799", "1800-2049", "2050"]}
]

PCIe_targets = [
    {"key": "PCIe_LPM", "devices":["NVM"], "lookup": "PCIe LPM Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "PCIe_Active", "devices":["NVM"], "lookup": "PCIe Link Active Summary - Sampled: Approximated Residency (Percentage)"}
]

DAQ_target = {
"P_SSD":-1,
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

picks = {'power_pick':MED, 'inferencingOnlyPower':False, 'sortSimilarData':False}






    
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

def createDataset(ID) :
    hobl_sets.append({
        "ID_path":ID,
        "data_label":ID,
        "data_type":[]
    })

def pullData(ID) :
    for item in hobl_sets:
        if (item["ID_path"] == ID) : 
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

# def add_etl(abs_path):
#     path_set = tools.splitLastItem(abs_path, "\\", 1)
#     dataset = pullData(path_set[0])
#     if dataset == None:
#         tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
#     if ETL not in dataset["data_type"] :
#         dataset["data_type"].append(ETL)
#     dataset["etl_path"] = abs_path


def add_power(tdic):
    ID = tdic['data_label']
    dataset = pullData(ID)
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + ID)
    if POWER not in dataset["data_type"] :
        dataset["data_type"].append(POWER)
    dataset["power_obj"] = psp.parsePowerSummaryCSV(tdic['power_summary_path'], DAQ_target)

    global file_num
    file_num += 1


def add_socwatch(tdic):
    ID = tdic['data_label']
    dataset = pullData(ID)
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + ID)
    if SOCWATCH not in dataset["data_type"] :
        dataset["data_type"].append(SOCWATCH)
    dataset["socwatch_obj"] = soc.parseSocwatch(tdic["socwatch_summary_path"], socwatch_targets)
    global file_num
    file_num += 1


def add_pcie_only(tdic):
    ID = tdic['data_label']
    dataset = pullData(ID)
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + ID)
    if SOCWATCH not in dataset["data_type"] :
        dataset["data_type"].append(SOCWATCH)
    dataset["pcie_socwatch_obj"] = psoc.parsePCIe(tdic["PCIe_socwatch_summary_path"], PCIe_targets)
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


def detectAndParseFile(file_list) :

    for tdic in file_list:
        if "data_label" in tdic:
            # print(tdic["data_label"])
            createDataset(tdic["data_label"])
        if "power_summary_path" in tdic:
            # print(tdic["power_summary_path"])
            add_power(tdic)
        if "socwatch_summary_path" in tdic:
            # print(tdic["socwatch_summary_path"])
            add_socwatch(tdic)
        if "PCIe_socwatch_summary_path" in tdic:
            # print("PCIe parser")
            add_pcie_only(tdic)

            
def main():
    detectAndParseFile(SWP)
    # pck.checkAndMarkPower(hobl_sets, picks)
    # if (picks["inferencing_power"] is True) : 
    # ===========================================================================
    # print processed(fully parsed) data to check the dictionary (Object) structure
    # since it is keep improving, changing
    # ===========================================================================
    print("====[hobl_sets]", hobl_sets)
    rpt.writeParsedInCSV(result_csv, hobl_sets, DAQ_target, socwatch_targets, PCIe_targets)


start_time = time.perf_counter()
main()
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Parsing {file_num} files Successful! [Elapsed time:::] {elapsed_time} seconds")







# ===========================================================================
# print processed(fully parsed) data above in the main() to check the dictionary (Object) structure
# since it is keep improving, changing. 
# ===========================================================================


