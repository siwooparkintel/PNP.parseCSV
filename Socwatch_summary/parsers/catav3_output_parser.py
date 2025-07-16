import parsers.tools as tools

def readTextfile(abs_path, CataV3_parsing_items) :

    with open(abs_path, 'r') as file:
        parsed = dict()
        for line in file:

            for item in CataV3_parsing_items:
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

        return parsed


def parseCataV3Results(abs_path, CataV3_parsing_items) :
    temp = dict()

    # print("========= in parseCataV3Resultes: ", abs_path)
    # temp['catav3_output_path'] = abs_path
    # temp['catav3_output_data'] = readTextfile(abs_path, CataV3_parsing_items)

    # if temp['catav3_output_data']['throughput'][1] == "" or temp['catav3_output_data']['latency_median'][1] == "":
    #     err = [abs_path, "=[ERROR]= : ", " it may not a result file or you may want to recollect"]
    #     temp['catav3_output_status'] = "failed"
    # else :
    #     temp['catav3_output_status'] = "successful"

    return temp





