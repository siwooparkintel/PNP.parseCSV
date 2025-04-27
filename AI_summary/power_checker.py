
import math

PICK_DATA = "MED" # "MIN", "MAX", "MED" all working






def markPicked(list):
    if len(list) > 0 :
        if len(list) == 1 or PICK_DATA == "MIN":
            list[0]['power_data']['picked'] = 'picked'
        elif PICK_DATA == "MAX":
            list[len(list)-1]['power_data']['picked'] = 'picked'
        elif PICK_DATA == "MED" and len(list)%2 == 0:
            list[int(len(list)/2)]['power_data']['picked'] = 'picked'
        elif PICK_DATA == "MED" and len(list)%2 == 1:
            list[math.floor(len(list)/2)]['power_data']['picked'] = 'picked'




def sortAndPick(objs) :
    etls = list()
    powers = list()
    socwatches = list()

    for obj in objs :
        dtype = obj["data_type"]
        if "ETL" in dtype and "POWER" in dtype:
            # if len(etls) > 0 and etls[leg(etls)]
            etls.append(obj)
        elif "SOCWATCH" in dtype and "POWER" in dtype:
            socwatches.append(obj)
        elif "POWER" in dtype:
            powers.append(obj)
    
    sorted_etls = sorted(etls, key=lambda x: x["power_data"]['P_SOC+MEMORY'])
    sorted_powers = sorted(powers, key=lambda x: x["power_data"]['P_SOC+MEMORY'])
    sorted_socwatches = sorted(socwatches, key=lambda x: x["power_data"]['P_SOC+MEMORY'])

    markPicked(sorted_etls)
    markPicked(sorted_powers)
    markPicked(sorted_socwatches)


    # sort working !!!
    # sorted_etls = sorted(etls, key=lambda x: x["power_data"]['P_SOC+MEMORY'], reverse=True)
    # sorted_powers = sorted(powers, key=lambda x: x["power_data"]['P_SOC+MEMORY'], reverse=True)
    # sorted_socwatches = sorted(socwatches, key=lambda x: x["power_data"]['P_SOC+MEMORY'], reverse=True)
    # print("+++++++++++++++++++++++++++", sorted_etls, sorted_powers, sorted_socwatches)


def pullSameLabel(whole_sets, label) :

    power_list = list()

    for block in whole_sets:

        if label == block["data_label"] : # and not ("ETL" in block["data_type"] or "SOCWATCH" in block["data_type"])
            temp = block["data_type"].copy()
            temp.reverse()
            block["power_data"]["power_type"] = "_".join(temp)
            #block["power_data"].update({"power_type": "===================================="})
            print("========", block['power_data']['P_SOC+MEMORY'])
            power_list.append(block)

    return power_list



def checkAndMarkPower(whole_sets) :

    done_model = set()

    for obj in whole_sets:
        
        if obj["data_label"] not in done_model:
            done_model.add(obj["data_label"])
            objs = pullSameLabel(whole_sets, obj["data_label"])
            sortAndPick(objs)
            #print(objs)
            
    
        


    


    print(f"=========== Hi! in checkAndMarkPower.py {len(whole_sets)} all data set looks good!")
