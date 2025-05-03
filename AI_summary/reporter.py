import csv
import tools



head_list = ["model_name"]

data_lines = []

data_vertical = []



def convertToVerticalData() :

    for i in range(len(data_lines[0])) :
        rail_line = list()
        for j in range(len(data_lines)) :
            rail_line.append(data_lines[j][i])

        data_vertical.append(rail_line)
        # this is the correct way/place to add empty line

        # if rail_line[0] == "Energy (J)":
            # Energy = rail_line
        # if rail_line[0] == "throughput (FPS)" or rail_line[0] == "Eng(J)/Frame":
            # FPS = rail_line
            # data_vertical.append([None] * len(data_lines))
        # elif rail_line[0] == "power_type":
        #     data_vertical.append([None] * len(data_lines))


# def addDevice() :
    
#     data_lines[0].insert(1, 'Device')

#     for index in range(len(lines)) :
#         line = data_lines[index]

#         if (index == 0) :
#             pass
#         else :
#             line.insert(1, line[device_index])



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



def writeParsedInCSV(file_path, hobl_data, AI_parsing_items, picks) :

    # head_list.append(None)
    # if "model_output_obj" not in hobl_data[0]:
    #     tools.errorAndExit("'model_output_obj' is not in the data, model_output parsing finished incorrectly" )


    with open(file_path, 'w', newline='') as file:

        writer = csv.writer(file)
        
        head_list = ["model_name"]

        power_list = hobl_data[0]['power_obj']['power_data']

        addPowerRailsToHeader(head_list, power_list)

        if "model_output_obj" in hobl_data[0]:
            addModelThroughputToHeader(head_list, AI_parsing_items)

        data_lines.append(head_list)


        for obj in hobl_data :

            # if "model_output_obj" not in obj:
            #     tools.errorAndExit("'model_output_obj' is not in the data, model_output parsing finished incorrectly: "+obj["data_label"])

            power_obj = obj["power_obj"]

            # print(obj, "===================================================")
  
            if picks['only_picks'] is False or (picks['only_picks'] is True and "picked" in power_obj):

                if power_obj["power_type"] in picks["report_picks"] :
                    data_line = list()
                    data_line.append(obj["data_label"])
                    for key in power_obj['power_data']:
                        # if key == "Eng(J)/Frame" and ''
                        data_line.append(power_obj['power_data'][key])
                    # data_line.append(None)

                    if "model_output_obj" in obj:
                        output_data = obj["model_output_obj"]['model_output_data']
                        for key in output_data:
                            data_line.append(output_data[key][0])
                        # writer.writerow(data_line)


                    # grouping similar AI model name next to each other for easier comparison 
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

        # addDevice()
        # addLines(['throughput (FPS)', 'Eng(J)/Frame'])

        if picks['data_direction'] == 'vertical':
            convertToVerticalData()
            writer.writerows(data_vertical)
        else :
            writer.writerows(data_lines)


        
        

