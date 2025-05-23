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

    if isInferencingFound == False :
        # print("======= not found: ", file_path, target_rail, data_set, step_avr)   
        return None                 
    
# print("======================================")

def getAveragePowerByRails(csv_list, time_scale, target_obj, throughput) :
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
            trace_data[rail] = round(sum(rail_list) / len(csv_list), 3)
            # print("==== ", rail, trace_obj[rail])
            # if rail == "P_SOC+MEMORY" :

    # print(trace_obj)
    trace_data["Energy (J)"] = round(trace_data["Run Time"] * trace_data["P_SOC+MEMORY"], 3)
    trace_data["Eng(J)/Frame"] = round(trace_data["Energy (J)"] / throughput, 3)
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

                block["trace_obj"]["trace_data"] = getAveragePowerByRails(csv_list[infer_start_idx:infer_end_idx], time_scale, target_obj, block["model_output_obj"]["model_output_data"]["throughput"][0])
                # print("========", block["trace_obj"]["trace_data"])
    # sub_slopes = list()
    # sub_deriv = list()
    # for infer_set in NPU_list :
    #     sub_slopes.append(infer_set[3])
    #     sub_deriv.append(infer_set[4])
    # sorted_slopes = sorted(sub_slopes)
    # sorted_deriv = sorted(sub_deriv)
    # print("slopes: ", sorted_slopes, "    derivatives: ", sorted_deriv)

def parsePowerTraceCSV(csv_path) :
    
    trace_data = None
    trace_obj = {"trace_data":trace_data}
    trace_obj["file_path"] = csv_path
    
    return trace_obj

"""
{'ID_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_002', 
'data_label': ['NPU', 'Model_C2_v1_2_1_qdq_proxy'], 
'data_type': ['POWER'], 
'power_obj': {
    'power_data': {
        'V_VAL_VCC_PCORE': 0.798799, 
        'I_VAL_VCC_PCORE': 1.050852, 'V_VAL_VCC_ECORE': 0.150996, 'I_VAL_VCC_ECORE': 0.026338, 'V_VAL_VCCSA': 1.11288, 'I_VAL_VCCSA': 5.715734, 'V_VAL_VCCGT': 0.000592, 'I_VAL_VCCGT': 3.7e-05, 'P_VCC_PCORE': 1.030715, 'P_VCC_ECORE': 0.014793, 'P_VCCSA': 6.907365, 'P_VCCGT': 7.2e-05, 'P_VCCL2': 0.000736, 'P_VCC1P8': 0.063183, 'P_VCCIO': 0.174757, 'P_VCCDDRIO': 0.157915, 'P_VNNAON': 0.078376, 'P_VNNAONLV': 0.004785, 'P_VDDQ': 0.079725, 'P_VDD2H': 1.042647, 'P_VDD2L': 0.002298, 'P_V1P8U_MEM': 0.061603, 'P_SOC+MEMORY': 9.619904, 'Run Time': 24.8, 'Energy (J)': 238.5736192, 'Eng(J)/Frame': 0.13266767088551282}, 
    'file_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_002\\AI_NPU_model_stripped_002\\AI_NPU_model_stripped_002_pacs-summary.csv', 
    'power_type': 'POWER', 
    'picked': 'picked'}, 
'trace_obj': {
    'trace_data': {'V_VAL_VCC_PCORE': 0.92805436645, 'I_VAL_VCC_PCORE': 1.20851033869, 'V_VAL_VCC_ECORE': 0.17722534819, 'I_VAL_VCC_ECORE': 0.02954816076, 'V_VAL_VCCSA': 1.2093717451400001, 'I_VAL_VCCSA': 7.052179581985, 'V_VAL_VCCGT': 0.000616341505, 'I_VAL_VCCGT': -3.158989e-05, 'P_VCC_PCORE': 1.1683267006, 'P_VCC_ECORE': 0.01611333995, 'P_VCCSA': 8.53572688394, 'P_VCCGT': 3.1879865e-05, 'P_VCCL2': 0.000837284245, 'P_VCC1P8': 0.07149115888999999, 'P_VCCIO': 0.204229451435, 'P_VCCDDRIO': 0.19398208713, 'P_VNNAON': 0.08283928151, 'P_VNNAONLV': 0.005073477020000001, 'P_VDDQ': 0.09819469445, 'P_VDD2H': 1.272967728105, 'P_VDD2L': 0.00212485188, 'P_V1P8U_MEM': 0.073973068115, 'P_SOC+MEMORY': 11.726846316795, 'Run Time': 20.0},
    'file_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_002\\AI_NPU_model_stripped_002\\AI_NPU_model_stripped_002_pacs-traces-100sr.csv'}, 
'model_output_obj': {
    'model_output_path': '\\\\10.54.63.126\\Pnpext\\Siwoo\\WW17.1_LNL32_ov20252\\test_data\\NPU\\Model_C2_v1_2_1_qdq_proxy\\AI_NPU_model_stripped_002\\NPU_Model_C2_v1_2_1_qdq_proxy_output.txt', 'model_output_data': {
        'read_model': [26.59, 'ms'], 'compile_model': [41.5, 'ms'], 'start_mem_usage': [126848.0, 'KB'], 'end_mem_usage': [145416.0, 'KB'], 'ram_used': [18568.0, 'KB'], 'first_inference': [4.24, 'ms'], 'device': ['NPU', ''], 'iterations': [35966.0, ''], 'duration': [20000.2, 'ms'], 'latency_median': [0.54, 'ms'], 'throughput': [1798.28, 'FPS']}, 'model_output_status': 'successful'}}, 

"""
