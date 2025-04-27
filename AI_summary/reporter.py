import csv



power_skip = ["picked", "file_path", "power_type"]

head_list = ["model_name"]

data_lines = []



def writeHorizontal() :
    for index in range(len(data_lines[0])):
        # col = []
        print("")




def writeParsedInCSV(file_path, hobl_data) :

    with open(file_path, 'w', newline='') as file:

        writer = csv.writer(file)
        
        head_list = ["model_name"]


        power_list = hobl_data[0]['power_data']

        model_output = hobl_data[0]['model_output_obj']['model_output_data']

        for key in power_list :
            if key not in power_skip:
                head_list.append(key)
        
        head_list.append(None)
        
        for key in model_output :
            head_list.append(f"{key} ({model_output[key][1]})")

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
                data_line.append(None)
                output_data = obj["model_output_obj"]['model_output_data']
                for key in output_data:
                    data_line.append(output_data[key][0])
                # writer.writerow(data_line)
                data_lines.append(data_line)

        for i in range(len(data_lines[0])) :
            rail_line = list()
            for j in range(len(data_lines)) :
                rail_line.append(data_lines[j][i])
            # data_column.append(rail_line)
            writer.writerow(rail_line)

        
        


        # writeHorizontal(file_path)



        # writer.writerow("")
        # writer.writerow("")
        # writer.writerows(failure_list)


