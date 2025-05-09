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

def socwatch_handler(block, header, soc_header_dict) :
    data_line = queryData(block['data_label'])
    # print("=====pulled: ", block['data_label'], data_line)
    if data_line is not None:
        socwatch_tables = block['socwatch_obj']['socwatch_tables']
        # print("=====socwatch_tables: ", socwatch_tables)
        for soc_key in soc_header_dict :
            soc_head = soc_header_dict[soc_key]
            table = getTableByLabel(socwatch_tables, soc_key)
            # print("=====pulled: ", soc_key, table)
            for s_key in soc_head :
                if table is not None and s_key in table['table_data'] :
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


def writeParsedInCSV(file_path, hobl_data, AI_parsing_items, picks) :
    
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['name']  
        socwatch_header_dict = soc.getSocwatchHeader()

        for block in hobl_data :
            # etl_block = None
            
            if picks['only_picks'] is False :
                # Todo
                print("every data goes into the CSV")
            elif "power_obj" in block and "picked" in block["power_obj"]:

                if "ETL" in block["data_type"] :
                    etl_handler(block)
                elif  "socwatch_obj" in block:
                    socwatch_handler(block, header, socwatch_header_dict)
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

        


                





"""
def writeParsedInCSV(file_path, hobl_data, AI_parsing_items, picks) :


    with open(file_path, 'w', newline='') as file:

        writer = csv.writer(file)
        
        head_list = ["model_name"]

        power_list = hobl_data[0]['power_obj']['power_data']

        addPowerRailsToHeader(head_list, power_list)

        if "model_output_obj" in hobl_data[0]:
            addModelThroughputToHeader(head_list, AI_parsing_items)

        data_lines.append(head_list)


        for obj in hobl_data :

            power_obj = obj["power_obj"]
            
            socwatch_obj = None

            if 'socwatch_obj' in obj :
                socwatch_obj = obj["socwatch_obj"]
            # print(obj, "===================================================")
  
            if picks['only_picks'] is False or (picks['only_picks'] is True and "picked" in power_obj):


                data_line = list()
                data_line.append(obj["data_label"])

                # ==================================================
                # Power Data 
                # ==================================================
                for key in power_obj['power_data']:
                    # if key == "Eng(J)/Frame" and ''
                    data_line.append(power_obj['power_data'][key])

                # ==================================================
                # Model Throughput Result Output
                # ==================================================
                # grouping similar AI model name next to each other for easier comparison 
                if "model_output_obj" in obj:
                    output_data = obj["model_output_obj"]['model_output_data']
                    for key in output_data:
                        data_line.append(output_data[key][0])
                similar_model = None

                for index in range(len(data_lines)-1, -1, -1):
                # for index in range(len(data_lines)):
                    if data_lines[index][0].find(data_line[0]) >= 0:
                        similar_model = index
                        break
                if similar_model is not None :
                    data_lines.insert(similar_model+1, data_line)
                else : 
                    data_lines.append(data_line)

                # ==================================================
                # Socwatch data 
                # ==================================================
            # if socwatch_obj is not None and socwatch_obj["power_type"] in picks["report_picks"] :
            #     for key in socwatch_obj['power_data']:
            #         # if key == "Eng(J)/Frame" and ''
            #         data_line.append(power_obj['power_data'][key])

        if picks['data_direction'] == 'vertical':
            convertToVerticalData()
            writer.writerows(data_vertical)
        else :
            writer.writerows(data_lines)

"""

# def addLines(target_heads) :

#     target_obj = dict()

#     # data_lines[0].insert(1, 'Device')

#     # detecting target head items
#     for idx in range(len(data_lines[0])) :
#         item = data_lines[0][idx]
#         #target_obj[item] = -1
        
#         if item in target_heads:
#             target_obj[item] = idx
       
#     for index in range(len(lines)) :
#         line = lines[index]

#         if (index == 0) :
#             pass
#         else :
#             line.insert(1, line[device_index])
