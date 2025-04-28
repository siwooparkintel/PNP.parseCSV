import os
import csv



# time table CSV file location, socwatch folder structure should follow in it
BA="\\\\[address]\\EC\\proj\\pst\\jf\\SPA-Lab\\Siwoo\\CatapultV3\\WW2511.5_CataV3_IT\\CataV3_IT\\Socwatch"


#======================================================================================
"""
To slice the Socwatch into web session
1. need to manually create time table CSV file. example file: "socwatch_time_table_CataV3_IT.csv"
2. "start" and "end" time is used ( the gap is the time difference in between DAQ power and ELT, if you use ETL to fill the table, gap should be 0)
3. actual socwatch should follow the folder structure\file_name
4. the calculated start and end time will be fed as --result-slice-range parameters
5. un-comment os.system line to batch file time table
"""
#======================================================================================


locals()["catav3_list"] = list()

with open(f"{BA}\\socwatch_time_table_CataV3_IT.csv", encoding='utf-8-sig', newline='') as file:
    for i in csv.DictReader(file):
        temp = dict(i)
        if temp['start'] != '' and temp['end'] != '' and temp['gap'] != '':
            temp['start'] = int((float(temp['start']) + float(temp['gap'])) * 1000)
            temp['end'] = int((float(temp['end']) + float(temp['gap']))  * 1000)
            if temp['start'] < 0 : temp['start'] = 0
            if temp['end'] < 0 : temp['end'] = 0
        print (type(temp), temp)

        locals()["catav3_list"].append(temp)


for item in locals()["catav3_list"] :
    #print(item['device'], item['inf_start'])
    if item['start'] >= 0 and item['end'] > 0 and item['end'] > item['start']: 
        
        print(f"socwatch -i {BA}\\{item['folder']}\\{item['folder2']}\\{item['file_name']} -o .\\ETLparsedSocWatch\\{item['index']}_{item['section']} --result-slice-range {item['start']},{item['end']} -r json")
        
        #================================================================================
        # un-comment this to run actual batch slicing
        #================================================================================
        #os.system(f"socwatch -i {BA}\\{item['folder']}\\{item['folder2']}\\{item['file_name']} -o .\\ETLparsedSocWatch\\{item['index']}_{item['section']} --result-slice-range {item['start']},{item['end']} -r json")
    else :
        print("=== this is not valid ==============", f"socwatch -i {BA}\\{item['folder']}\\{item['folder2']}\\{item['file_name']} -o .\\ETLparsedSocWatch\\{item['index']}_{item['section']} --result-slice-range {item['start']},{item['end']} -r json")



