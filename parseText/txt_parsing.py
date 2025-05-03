import os
import csv
import re
import sys


current_folder = os.getcwd()


# =======================================================
# if you need to use hardcoded way to feed the data, do it here
# =======================================================

BA = os.getcwd()
#result_list_csv = f"{BA}\\file_list.csv"


# =======================================================
# final output file location, if you want to make it
# in the same folder, remove "..\\"
# =======================================================
parsed_csv = f"{BA}\\txt_perf_parsed_results.csv"

model_list = list()
result_list = list()
failure_list = list()


# =======================================================
# add here more strings that you want to detect
# currentl it only detects floating numbers. 
# if you need to include text parsing, modify parseNumberic function
# =======================================================
parsing_items = [
    {"key": "read_model", "lookup": "[ INFO ] Read model took", "unit":"ms"},
    {"key": "compile_model", "lookup": "[ INFO ] Compile model took", "unit":"ms"},
    {"key": "start_mem_usage", "lookup": "[ INFO ] Start of compilation memory usage:", "unit":"KB"},
    {"key": "end_mem_usage", "lookup": "[ INFO ] End of compilation memory usage:", "unit":"KB"},
    {"key": "ram_used", "lookup": "[ INFO ] Compile model ram used", "unit":"KB"},
    {"key": "first_inference", "lookup": "[ INFO ] First inference took", "unit":"ms"},
    {"key": "latency_median", "lookup": "[ INFO ]    Median:", "unit":"ms"},
    {"key": "throughput", "lookup": "[ INFO ] Throughput", "unit":"FPS"}
]

# =======================================================
# currently it only parsing numeric values.
# if you want to parse text, expand the function here
# =======================================================
def parseNumeric(text) :
    return ''.join(re.findall(r'[0-9.]', text))


def get_model_list(path, target_ext) :

    # print("=========== in get_model_list: ", path)
    dir_list = os.listdir(path)
    # print("=========== in get_model_list: ", dir_list)

    for file_name in dir_list :

        tfile = dict()
        file_comp = file_name.split(".")
        tfile["name"] = ".".join(file_comp[:-1])
        tfile["extension"] = file_comp[len(file_comp)-1]
        
        if (tfile["extension"].lower()) == target_ext.lower():
            model_list.append(tfile)

    print(model_list, "==== total detected file ==== : ",len(model_list))



def readTextfile(txtDic) :
    # print (type(txtDic), txtDic)
    # if txtDic['index'] < 1:
        with open(".".join(txtDic.values()), 'r') as file:
            parsed = dict()
            for line in file:
                # print(type(line), line)
                for item in parsing_items:
                    #print(type(item), item)
                    target_text = item["lookup"]
                    found = line.rfind(target_text)
                    parsed_num = parseNumeric(line)
                    if found >= 0 and parsed_num != '' :
                        parsed[item["key"]] = [float(parsed_num), item['unit']]
                        # print("[SI] ====================", parsed)

            return parsed


# =======================================================
# use this if you want to detect all files in the same folder
# =======================================================
def loadModelResults(file_list) :

    for index, file in enumerate(file_list):
        
        temp = dict()

        #print("======= in loadModelResults: ", file, " === index : ", index )

        if file['name'] != '' :
            temp['file_name'] = ".".join(file.values())
            temp["index"] = index
            temp['parsed'] = readTextfile(file)
            if temp['parsed'] is not None and len(temp['parsed']) < len(parsing_items) :
                err = [".".join(file.values()), "=[ERROR]= : ", " it may not a result file or you may want to recollect"]
                print(err)
                temp['test_status'] = "failed"
                failure_list.append(err)
            else :
                temp['test_status'] = "successful"
                result_list.append(temp)

    print("===================================================================")
    print(result_list)
    print("===================================================================")


# =======================================================
# if you want to feed CSV data, use this
# It is expecting CSV header "file_name"
# =======================================================
def loadModelCSVresults(csv_list) :
    with open(csv_list, encoding='utf-8-sig', newline='') as file:
        for index, i in enumerate(csv.DictReader(file)):
            temp = dict(i)

            if temp.get('file_name') is None:
                print("=============================================================================")
                sys.exit("[ERROR] No 'file_name' in the CSV header, you may want to add the header")
                print("=============================================================================")

            if temp['file_name'] != '' :
                temp['file_name'] = temp['file_name'].strip()
                temp["index"] = index
                temp['parsed'] = readTextfile(temp)
                if temp['parsed'] is not None and len(temp['parsed']) < len(parsing_items) :
                    err = [temp['file_name'], "=[ERROR]= : ", " it may not a result file or you may want to recollect"]
                    print(err)
                    temp['test_status'] = "failed"
                    failure_list.append(err)
                else :
                    temp['test_status'] = "successful"
                    result_list.append(temp)

    print("===================================================================")
    print(result_list)
    print("===================================================================")


# =======================================================
# write parsed data in a CSV file that 'parsed_CSV' specified
# successful parsing first, then failed list 
# =======================================================

def writeParsedInCSV(file_path) :

    with open(file_path, 'w', newline='') as file:

        writer = csv.writer(file)
        
        head_list = ["model_name"]
        example = result_list[0]['parsed']
        for key in example :
            head_list.append(f"{key} ({example[key][1]})")
        
        writer.writerow(head_list)

        for model_result in result_list :
            if model_result['test_status'] == 'successful' :
                data = [model_result['file_name']]
                for key in model_result['parsed'] :
                    data.append(model_result['parsed'][key][0])
                writer.writerow(data)
        
        writer.writerow("")
        writer.writerow("")
        writer.writerows(failure_list)



def main():

    get_model_list(BA, "txt")
    loadModelResults(model_list)
    writeParsedInCSV(parsed_csv)


main()

# =======================================================
# example of the parsed result data structure
# =======================================================
'''
# model_parsed data structure
{
'file_name': 'bm0329_Model_A3_1_2_0_qdq_proxy_output.txt',
'index': 0,
'parsed': {
    'read_model': [9.02, 'ms'],
    'compile_model': [24.34, 'ms'], 
    'start_mem_usage': [302696.0, 'KB'],
    'end_mem_usage': [307568.0, 'KB'],
    'ram_used': [4872.0, 'KB'], 
    'first_inference': [2.55, 'ms'], 
    'latency_median': [0.18, 'ms'], 
    'throughput': [5393.15, 'FPS']
    }, 
'test_status': 'successful'
}
'''
