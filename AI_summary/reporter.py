import csv
import tools
import socwatch_summary_parser as soc


head_list = ["model_name"]

data_lines = []

data_vertical = []


def queryData(data_label) :
    data_line = None
    for line_index in range(len(data_lines)-1, -1, -1):
        line = data_lines[line_index]
        if data_label == line[0] :
            data_line = line
            break
    return data_line

def convertToVerticalData() :
    for i in range(len(data_lines[0])) :
        rail_line = list()
        for j in range(len(data_lines)) :
            rail_line.append(data_lines[j][i])
        data_vertical.append(rail_line)

def addPowerRailsToHeader(head_list, power_list) :
    for key in power_list :
        head_list.append(key)

def addModelThroughputToHeader(head_list, AI_parsing_items) :
    # model_output = hobl_data[0]['model_output_obj']['model_output_data']
    for index in range(len(AI_parsing_items)) :
        key = AI_parsing_items[index]["key"]
        if key == "device" or key == "iterations":
            head_list.append(f"{key}")
        else :
            head_list.append(f"{key} ({AI_parsing_items[index]["unit"]})")


def etl_handler(block) :
    pass

def getTableByLabel(socwatch_tables, soc_key) :
    tbox = None
    for table in socwatch_tables :
        if soc_key == table['label'] :
            tbox = table
            break
    return tbox

def socwatch_handler(block, socwatch_targets, soc_header_dict) :
    data_line = queryData(block['data_label'])
    # print("=====pulled: ", block['data_label'], data_line)
    if data_line is not None:
        socwatch_tables = block['socwatch_obj']['socwatch_tables']
        # print("=====socwatch_tables: ", socwatch_tables)
        for soc_key in soc_header_dict :
            soc_head = soc_header_dict[soc_key]
            table = getTableByLabel(socwatch_tables, soc_key)
            buckets = next((item for item in socwatch_targets if item['key'] == soc_key and "buckets" in item), None)
            # print("=====pulled: ", soc_key, table)
            for s_key in soc_head :
                # print("== found buckets: ", soc_key, buckets)
                ranges = s_key.split("-")
                if table is not None and buckets is not None and len(ranges) == 2:
                    min = int(ranges[0])
                    max = int(ranges[1])
                    copied = table['table_data'].copy()
                    copied.pop(next(iter(copied)))
                    total = sum([float(copied[key]) for key in copied if int(key) >= min and int(key) <= max])
                    # print([float(copied[key]) for key in copied if int(key) >= min and int(key) <= max])
                    # print("== found buckets: ", table['table_data'], copied, ranges, total)
                    data_line.append(total)
                elif table is not None and s_key in table['table_data'] :
                    data_line.append(table['table_data'][s_key])
                else :
                    data_line.append(None)

def power_output_handler(data_line, block, header) :
    power_obj = block["power_obj"]
    for key in power_obj['power_data']:
        data_line.append(power_obj['power_data'][key])
        if len(data_lines) == 0:
            header.append(key)
            # pass 
    if "model_output_obj" in block:
        output_data = block["model_output_obj"]['model_output_data']
        for key in output_data:
            data_line.append(output_data[key][0])
            if len(data_lines) == 0:
                header.append(key)
                # pass

def getSocwatchHeaderList(soc_dict) :
    soc_list = list()
    for key in soc_dict :
        soc_list.extend(soc_dict[key])
    return soc_list


def writeParsedInCSV(file_path, hobl_data, socwatch_targets, picks) :
    
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['name']  
        socwatch_header_dict = soc.getSocwatchHeader(socwatch_targets)

        for block in hobl_data :
            # etl_block = None
            
            if picks['only_picks'] is False :
                # Todo
                print("every data goes into the CSV")
            elif "power_obj" in block and "picked" in block["power_obj"]:

                if "ETL" in block["data_type"] :
                    etl_handler(block)
                elif  "socwatch_obj" in block:
                    socwatch_handler(block, socwatch_targets, socwatch_header_dict)
                else :
                    data_line = [block["data_label"]]
                    power_output_handler(data_line, block, header)

                    similar_model = None
                    for index in range(len(data_lines)-1, -1, -1):
                        if data_lines[index][0].find(data_line[0]) >= 0:
                            similar_model = index
                            break
                    if similar_model is not None :
                        data_lines.insert(similar_model+1, data_line)
                    else : 
                        data_lines.append(data_line)

        socwatch_header = getSocwatchHeaderList(socwatch_header_dict)
        header.extend(socwatch_header)
        data_lines.insert(0, header)

        if picks['data_direction'] == 'vertical':
            convertToVerticalData()
            writer.writerows(data_vertical)
        else :
            writer.writerows(data_lines)
        
        # writer.writerows(data_lines)

        


                



