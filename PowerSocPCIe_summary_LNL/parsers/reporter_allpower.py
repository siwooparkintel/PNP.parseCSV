import pandas as pd
import parsers.tools as tools



def flatten_data(entry, picks, socwatch_targets, PCIe_targets):
    flattened = {'data_label': entry['data_label'], 'condition': entry['condition']}
    flattened.update(tools.flatten_power_dic(entry, picks))
    flattened.update(tools.flatten_socwatch_dic(entry, socwatch_targets))
    flattened.update(tools.flatten_pcie_socwatch_dic(entry, PCIe_targets))
    return flattened


def reportAllPowerAndType2(result_path, hobl_data, picks, socwatch_targets, PCIe_targets) :
    df = pd.DataFrame([flatten_data(entry, picks, socwatch_targets, PCIe_targets) for entry in hobl_data])
    df.to_excel(result_path+"_allPower_h.xlsx", index=False)

    df_v = df.transpose()
    df_v = df_v.reset_index()
    df_v.rename(columns={'index': 'Attribute'}, inplace=True)
    df_v.to_excel(result_path+"_allPower_v.xlsx", index=False)




    




        


                



