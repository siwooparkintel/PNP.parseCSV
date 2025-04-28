import re
import tools




# def set_parsing_items(lists) :
#     parsing_items = lists
#     #print("[parsing_items] :: ", parsing_items)



def readTextfile(abs_path, AI_parsing_items) :
    # print ("===== in readTextFile :: ", abs_path)
    # if txtDic['index'] < 1:
    with open(abs_path, 'r') as file:
        parsed = dict()
        for line in file:
            # print(type(line), line)
            # d_found = line.rfind("[ INFO ] Execution Devices:")

            # if d_found >=0:
            #     # print(line)
            #     # parsed['device'] = [line[d_found:].split("'")[1], ""]
            #     parsed['device'] = [line[len():].split("'")[1], ""]
            #     # parsed['device'] = [line[d_found:].split("'")[1], ""]

            for item in AI_parsing_items:
                #print(type(item), item)
                target_text = item["lookup"]
                found = line.rfind(target_text)
                if found >= 0 :
                    target_string = line[len(target_text):]
                    parsed_data = ""
                    if item['key'] == 'device':
                        parsed_data = tools.parseDevice(target_string)
                    else :
                        parsed_data = float(tools.parseNumeric(target_string))
                    parsed[item["key"]] = [parsed_data, item['unit']]
                    break
                elif item["key"] not in parsed:
                    parsed[item["key"]] = [None, ""]
                
                
            
        # print("[SI] ====================", parsed)

        return parsed


def parseModelResults(abs_path, AI_parsing_items) :
    # print("=== before: ", abs_path)
    temp = dict()

    temp['model_output_path'] = abs_path
    temp['model_output_data'] = readTextfile(abs_path, AI_parsing_items)
    # if temp['parsed'] is not None and len(temp['parsed']) < len(parsing_items) :
    if 'throughput' not in temp['model_output_data'] or 'latency_median' not in temp['model_output_data']:
        err = [abs_path, "=[ERROR]= : ", " it may not a result file or you may want to recollect"]
        temp['model_output_status'] = "failed"
    else :
        temp['model_output_status'] = "successful"
    # print("=== after: ", temp)

    return temp



"""
def get_model_list(path, target_ext) :

    dir_list = os.listdir(path)

    for file_name in dir_list :

        tfile = dict()
        file_comp = file_name.split(".")
        tfile["name"] = ".".join(file_comp[:-1])
        tfile["extension"] = file_comp[len(file_comp)-1]
        
        if (tfile["extension"].lower()) == target_ext.lower():
            model_list.append(tfile)

    print(model_list, "==== total detected file ==== : ",len(model_list))

    
def loadModelCSVresults(csv_list) :
    with open(csv_list, encoding='utf-8-sig', newline='') as file:
        for index, i in enumerate(csv.DictReader(file)):
            temp = dict(i)

            if temp.get('file_name') is None:
                errorAndExit("No 'file_name' in the CSV header, you may want to add the header")


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

"""

# =======================================================
# example of the parsed result data structure
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



