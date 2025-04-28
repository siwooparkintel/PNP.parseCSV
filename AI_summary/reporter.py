import csv
import tools



power_skip = ["picked", "file_path", "power_type"]

head_list = ["model_name"]

data_lines = []

data_vertical = []



def convertToVerticalData() :
    Energy = list()
    FPS = list()
    for i in range(len(data_lines[0])) :
        rail_line = list()
        for j in range(len(data_lines)) :
            rail_line.append(data_lines[j][i])

        data_vertical.append(rail_line)
        # this is the correct way/place to add empty line
        if rail_line[0] == "Energy (J)":
            Energy = rail_line
            data_vertical.append([None] * len(data_lines))
        elif rail_line[0] == "throughput (FPS)":
            FPS = rail_line
            data_vertical.append([None] * len(data_lines))

        # duplicate the device info on the second top of the data
        if rail_line[0] == 'device':
            data_vertical.insert(1, rail_line)  
    # print(Energy, FPS, "***********************")
    eng_fps_line = list()
    for index in range(len(Energy)) :
        if index == 0:
            eng_fps_line.append("Eng(J)/FPS")
        elif Energy[index] is not None and FPS[index] is not None :
            eng_fps_line.append(Energy[index] / FPS[index])
        else :
            eng_fps_line.append(None)
    data_vertical.append(eng_fps_line)


def writeParsedInCSV(file_path, hobl_data, AI_parsing_items) :

    with open(file_path, 'w', newline='') as file:

        writer = csv.writer(file)
        
        head_list = ["model_name"]


        power_list = hobl_data[0]['power_data']

    
        for key in power_list :
            if key not in power_skip:
                head_list.append(key)
        
        # head_list.append(None)
        if "model_output_obj" not in hobl_data[0]:
            tools.errorAndExit("'model_output_obj' is not in the data, model_output parsing finished incorrectly" )

        # model_output = hobl_data[0]['model_output_obj']['model_output_data']
        for index in range(len(AI_parsing_items)) :
            key = AI_parsing_items[index]["key"]
            if key == "device" or key == "iterations":
                head_list.append(f"{key}")
            else :
                head_list.append(f"{key} ({AI_parsing_items[index]["unit"]})")

        # writer.writerow(head_list)

        data_lines.append(head_list)


        for obj in hobl_data :
            power_data = obj["power_data"]
            data_line = list()
            if "picked" in power_data and power_data["power_type"] == "POWER":
                data_line.append(obj["data_label"])
                for key in power_data:
                    if key not in power_skip: 
                        data_line.append(power_data[key])
                # data_line.append(None)

                if "model_output_obj" not in obj:
                    tools.errorAndExit("'model_output_obj' is not in the data, model_output parsing finished incorrectly" )

                output_data = obj["model_output_obj"]['model_output_data']
                for key in output_data:
                    data_line.append(output_data[key][0])
                # writer.writerow(data_line)


                # grouping similar AI model name next to each other for easier comparison 
                similar_model = None
                for index in range(len(data_lines)):
                    if data_lines[index][0].find(data_line[0]) >= 0:
                        similar_model = index
                        break
                if similar_model is not None :
                    data_lines.insert(similar_model+1, data_line)
                else : 
                    data_lines.append(data_line)



        # writer.writerows(data_line)

        convertToVerticalData()
        writer.writerows(data_vertical)

        
        

