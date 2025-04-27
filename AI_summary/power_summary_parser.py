import csv
import tools

target = {
"V_VAL_VCC_PCORE":0,
"I_VAL_VCC_PCORE":0,
"V_VAL_VCC_ECORE":0,
"I_VAL_VCC_ECORE":0,
"V_VAL_VCCSA":0,
"I_VAL_VCCSA":0,
"V_VAL_VCCGT":0,
"I_VAL_VCCGT":0,
"P_VCC_PCORE":0,
"P_VCC_ECORE":0,
"P_VCCSA":0,
"P_VCCGT":0,
"P_VCCL2":0,
"P_VCC1P8":0,
"P_VCCIO":0,
"P_VCCDDRIO":0,
"P_VNNAON":0,
"P_VNNAONLV":0,
"P_VDDQ":0,
"P_VDD2H":0,
"P_VDD2L":0,
"P_V1P8U_MEM":0,
"P_SOC+MEMORY":0,
"Run Time":0
}

fields = []
rows = []

AVERAGE = "Average"



def parsePowerSummaryCSV(csv_path) :
    
    power_collection = dict()
    # reading csv file
    with open(csv_path, encoding='utf-8-sig', newline='') as csvfile:
        
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        fields = next(csvreader)
        
        # printing the field names
        # print('Field names are:' + ', '.join(field for field in fields))

        avr_index = -1
        try:
            avr_index = fields.index(AVERAGE)
        except:
            tools.errorAndExit(f"{AVERAGE} is NOT in the CSV header")

        
        # print("=======", csvreader)
        for row in csvreader:
            rows.append(row)

        power_len = len(rows)-1
        for target_rail in target:
            #print(type(rail), rail)
            
            for power_rail_index in range(len(rows)-1, -1, -1):
                t_rail = rows[power_rail_index]
                # print(power_rail_index, type(rows[power_rail_index]), rows[power_rail_index], target_rail)
                if t_rail[0]== target_rail:
                    power_collection[target_rail] = float(t_rail[avr_index])
                    break

        power_collection['file_path'] = csv_path
        # power_collection['data_type'] 
        return power_collection



    # for row in rows[len(rows)-len(target):]:
    #     # parsing each column of a row
    #     print(type(row), row)





        # for col in row:
            # print(type(col), "====", col)
            # print("%10s" % col, end=" "),


    
        # for index, i in enumerate(csv.DictReader(file)):
        #     temp = dict(i)
        #     print(type(temp), temp)

        # for i in range(len(csv.DictReader(file)) - 1, -1, -1):
        #     temp = dict(i)
        #     print(temp)


        # for index, i in enumerate(csv.DictReader(file)):
        #     temp = dict(i)

        #     if temp.get('Name') is None or temp.get('Average'):
        #         tools.errorAndExit("No 'Name' or 'Average 'in the CSV header")


        #     if temp['Name'] != '' :
        #         temp['Name'] = temp['Name'].strip()
        #         temp['parsed'] = readTextfile(temp)
        #         if temp['parsed'] is not None and len(temp['parsed']) < len(parsing_items) :
        #             err = [temp['file_name'], "=[ERROR]= : ", " it may not a result file or you may want to recollect"]
        #             print(err)
        #             temp['test_status'] = "failed"

        #         else :
        #             temp['test_status'] = "successful"


    # print("===================================================================")

    # print("===================================================================")

