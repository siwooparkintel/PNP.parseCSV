import pandas as pd
import parsers.tools as tools



def flatten_data(entry, picks, socwatch_targets, PCIe_targets):
    flatten_list = list()
    flattened = {'data_label': entry['data_label'], 'condition': entry['condition']}
    flattened.update(tools.flatten_power_dic(entry, picks))
    flattened_socwatch_list = tools.flatten_socwatch_dic(entry, socwatch_targets)
    flattened.update(flattened_socwatch_list[0])
    flattened.update(tools.flatten_pcie_socwatch_dic(entry, PCIe_targets))
    flatten_list.append(flattened)
    flatten_list.extend(flattened_socwatch_list[1:]) if len(flattened_socwatch_list) > 1 else None
    return flatten_list


def reportAllPowerAndType2(result_path, hobl_data, picks, socwatch_targets, PCIe_targets) :
    data_list = list()
    for entry in hobl_data :
        data_list.extend(flatten_data(entry, picks, socwatch_targets, PCIe_targets))
    df = pd.DataFrame(data_list)
    df.to_excel(result_path+"_allPower_h.xlsx", index=False)

    df_v = df.transpose()
    df_v = df_v.reset_index()
    df_v.rename(columns={'index': 'Attribute'}, inplace=True)
    df_v.to_excel(result_path+"_allPower_v.xlsx", index=False)




    




        


                



