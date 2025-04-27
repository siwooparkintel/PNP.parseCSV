
import os
from os import listdir
from os.path import isfile, join
import tools
import model_output_parser as mop
import socwatch_summary_parser as soc
import power_summary_parser as psp
import power_checker as pck
import reporter as rpt




#BASE = os.getcwd()
BASE = "\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\GPU"

#result_list_csv = f"{BA}\\file_list.csv"
parsed_csv = f"{BASE}\\..\\AI_models_parsed_results.csv"

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
    dataset["model_output_obj"] = mop.parseModelResults(abs_path)

def add_power(abs_path):
    path_set = tools.splitLastItem(abs_path, "\\", 1)
    dataset = pullData(path_set[0])
    if dataset == None:
        tools.errorAndExit("pulling data failed by using the Path as ID: " + abs_path)
    if POWER not in dataset["data_type"] :
        dataset["data_type"].append(POWER)
    dataset["power_data"] = psp.parsePowerSummaryCSV(abs_path)

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
    elif f.find(CL_OUTPUT) >= 0 and f.find(CL_AI_MODEL) >= 0 :
        #print("AI_model output detected ", abs_path, f)
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
        #print("================", abs_path)

        if f == "Model_E_v1_2_0_qdq_proxy_stripped":
            break

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
    print("====[hobl_sets]", hobl_sets)
    

    rpt.writeParsedInCSV(parsed_csv, hobl_sets)


main()




# =======================================================
# example of the parsed model output result data structure
# =======================================================
'''
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