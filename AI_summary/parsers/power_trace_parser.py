import csv
import parsers.tools as tools


fields = []
rows = []

AVERAGE = "Average"

# time buffer to include the whole inferencing duration. 
# inferencing happening at the end of power collection, 
# so it is easier to check it from the power data backwards
# power data collection ends after 2.2 seconds in most of the time, + 2.8 seconds more buffer, total 5000 ms.
TIME_BUFFER = 5000


def getSamplingRate(file_path) :
    # file_name = file_path.split("\\")[-1]
    samplingRate = file_path.split("-")[-1]
    # print(float(tools.parseNumeric(samplingRate)))
    return float(tools.parseNumeric(samplingRate))


def getTargetedRailIndexObject(header, DAQ_target) :
    copied = DAQ_target.copy()
    for target_rail_name in copied :
        for trace_idx in range(len(header)-1, -1, -1):
            if target_rail_name == header[trace_idx] :
                copied[target_rail_name] = trace_idx
                break
    return copied

def getReversedPower(csv_list, total_row_num, infer_duration, time_scale, power_rail_name) :
    # capture power data in reverse since the inferencing happens at the end of the power collection
    target_power_reversed = list()
    stop_row_num = total_row_num - (int((infer_duration+TIME_BUFFER) / time_scale))
    for idx in range(total_row_num-1, stop_row_num, -1):
        line = csv_list[idx]
        target_power_reversed.append(line[power_rail_name])
    # print(target_power_reversed, len(target_power_reversed))    
    return target_power_reversed

def getInferencingStartReversed(target_power_reversed, target_rail, file_path) :

          
    # now have to find the power surge by checking power changes (slope and derivative)
    step_avr = list()
    steps = 10
    length = len(target_power_reversed)-1
    isInferencingFound = False

    for idx in range(0, length, steps) :
        upto = idx + steps
        if upto > length :
            upto = length
            
        # data_set will be 5 item list : [index start, idx end, step average, slope, derivative]
        data_set = [idx, upto]

        total = sum([float(item) for item in target_power_reversed[idx:upto]])

        # ==========================================================================================================
        # data correction. physical power measurement can give the impossible negative power in very miniscule scale
        # adjust is needed to avoid Zero related issues
        # ==========================================================================================================
        total = 0.001 if total < 0.001 else total    # if you set smaller than 0.001 it became 0 divided by Zero later
        data_set.append(round(total/len(target_power_reversed[idx:upto]), 4))
        step_avr_idx = len(step_avr)-1
        if step_avr_idx == -1:
            data_set.append(1)
            data_set.append(0)
            step_avr.append(data_set)
        else :
            # print(step_avr[step_avr_idx],  step_avr[step_avr_idx-1], step_avr[step_avr_idx] - step_avr[step_avr_idx-1])
            # slope = step_avr[key][step_avr_idx] / step_avr[step_avr_idx-1] if step_avr[step_avr_idx-1] else 0
            # derivative = step_avr[step_avr_idx] - step_avr[step_avr_idx-1]
            pre_data_set = step_avr[-1]
            # print ("===================== : ", pre_data_set)
            slope = round(data_set[2] / pre_data_set[2], 2)
            derivative = round((data_set[2] - pre_data_set[2]), 2)
            data_set.append(slope)
            data_set.append(derivative)
            step_avr.append(data_set)
            if slope > target_rail[1] and derivative > target_rail[2]:
                isInferencingFound = True
                # print("== found inferencing start", file_path, target_rail, data_set, step_avr)
                return data_set[0]


                break

    if isInferencingFound == False :
        # print("======= not found: ", file_path, target_rail, data_set, step_avr)   
        return None                 
    
# print("======================================")

def getAveragePowerByRails(csv_list, time_scale, target_obj) :
    trace_data = dict()
    for rail in target_obj:
        # print("==== rail name: ", len(csv_list), rail, target_obj[rail])
        rail_idx = target_obj[rail]
        if rail == "Run Time" : 
            trace_data["Run Time"] = round((len(csv_list) * time_scale / 1000), 1) # in seconds 1st floating digit 
        else :
            rail_list = [float(line[rail_idx]) for line in csv_list]
            # if rail == "P_SOC+MEMORY" :
            #     print(rail, rail_list)
            trace_data[rail] = sum(rail_list) / len(csv_list)
            # print("==== ", rail, trace_obj[rail])
            # if rail == "P_SOC+MEMORY" :


    # print(trace_obj)
    return trace_data






def averageInferencingPower(hobl_data, DAQ_target) :
    # reading csv file

    for block in hobl_data:

        if "data_type" in block and len(block["data_type"]) == 1 and "POWER" in block["data_type"] and "power_obj" in block and "picked" in block["power_obj"] and "model_output_obj" in block and block["model_output_obj"]["model_output_status"] == "successful":
            
            block["trace_obj"]
            trace_sampling_rate = getSamplingRate(block["trace_obj"]["file_path"])
            # in milliseconds. So 100 sampling rate, 1 row advance means 10 ms passed.
            time_scale = 1000 / trace_sampling_rate
            

            with open(block["trace_obj"]["file_path"], encoding='utf-8-sig', newline='') as tracefile:
                
                csvreader = csv.reader(tracefile)
                header = next(csvreader)
                target_obj = getTargetedRailIndexObject(header, DAQ_target)
                infer_duration = block["model_output_obj"]["model_output_data"]["duration"][0] 
                device = block["model_output_obj"]["model_output_data"]["device"][0]
                csv_list = list(csvreader)
                total_row_num = len(csv_list)
                # CPU uses P-core for inferencing, so default. 
                # [Power_rail_name, slope minimum, power delta minimum]
                target_rail = ["P_VCC_PCORE", 3, 3]
                if "GPU" in device:
                    target_rail = ["P_VCCGT", 2.5, 2.5]  # after checking 50 files 
                elif "NPU" in device:
                    target_rail = ["P_VCCSA", 2.6, 1.38]
                
                infer_start_idx = -1
                infer_end_idx = -1

                target_power_reversed = getReversedPower(csv_list, total_row_num, infer_duration, time_scale, target_obj[target_rail[0]])
                infer_start_reversed = getInferencingStartReversed(target_power_reversed, target_rail, block["trace_obj"]["file_path"])
                infer_duration_in_scale = round((infer_duration / time_scale))
                infer_start_idx = total_row_num - infer_duration_in_scale - infer_start_reversed
                infer_end_idx = infer_start_idx + infer_duration_in_scale

                block["trace_obj"]["trace_data"] = getAveragePowerByRails(csv_list[infer_start_idx:infer_end_idx], time_scale, target_obj)
          

    # sub_slopes = list()
    # sub_deriv = list()
    # for infer_set in NPU_list :
    #     sub_slopes.append(infer_set[3])
    #     sub_deriv.append(infer_set[4])
    # sorted_slopes = sorted(sub_slopes)
    # sorted_deriv = sorted(sub_deriv)
    # print("slopes: ", sorted_slopes, "    derivatives: ", sorted_deriv)


                # # getting target index
                # for power_rail_index in range(len(header)-1, -1, -1):
                #     if header[power_rail_index] == "P_SOC+MEMORY":
                #         target_idx = power_rail_index
                #         break
                
                # for line in range(len(list(csvreader))-1, -1, -1):
                #     target_power.append(line[target_idx])

                
                




                # print(header)


                # avr_index = -1
                # try:
                #     avr_index = fields.index(AVERAGE)
                # except:
                #     tools.errorAndExit(f"{AVERAGE} is NOT in the CSV header")

                
                # # print("=======", csvreader)
                # for row in csvreader:
                #     rows.append(row)

                # power_len = len(rows)-1
                # for target_rail in DAQ_target:
                #     #print(type(rail), rail)
                    
                #     for power_rail_index in range(len(rows)-1, -1, -1):
                #         t_rail = rows[power_rail_index]
                #         # print(power_rail_index, type(rows[power_rail_index]), rows[power_rail_index], target_rail)
                #         if t_rail[0]== target_rail:
                #             power_data[target_rail] = float(t_rail[avr_index])
                #             break

                # power_data['Energy (J)'] = power_data["P_SOC+MEMORY"] * power_data["Run Time"]
                # # power_data['Eng(J)/Frame'] = None

                # power_obj['file_path'] = csv_path
                # # power_collection['data_type'] 



def parsePowerTraceCSV(csv_path) :
    
    trace_data = None
    trace_obj = {"trace_data":trace_data}
    trace_obj["file_path"] = csv_path
    
    return trace_obj


