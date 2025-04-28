import csv
import tools



fields = []
rows = []

AVERAGE = "Average"



def parsePowerSummaryCSV(csv_path, DAQ_target) :
    
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
        for target_rail in DAQ_target:
            #print(type(rail), rail)
            
            for power_rail_index in range(len(rows)-1, -1, -1):
                t_rail = rows[power_rail_index]
                # print(power_rail_index, type(rows[power_rail_index]), rows[power_rail_index], target_rail)
                if t_rail[0]== target_rail:
                    power_collection[target_rail] = float(t_rail[avr_index])
                    break

        power_collection['Energy (J)'] = power_collection["P_SOC+MEMORY"] * power_collection["Run Time"]


        power_collection['file_path'] = csv_path
        # power_collection['data_type'] 
        return power_collection



