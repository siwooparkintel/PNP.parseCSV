import parsers.reporter_allpower as rap
import parsers.reporter_picked as rpick
import parsers.reporter_inferenceOnly as rinf




def writeParsedInCSV(result_path, hobl_data, picks, socwatch_targets, PCIe_targets) :
    
    print(hobl_data)

    rap.reportAllPowerAndType2(result_path, hobl_data, picks, socwatch_targets, PCIe_targets)
    # rpick.reportPickedData2(result_path, hobl_data, socwatch_targets, picks)
    # rinf.reportInferencingOnlyPower(result_path, hobl_data, DAQ_target) if picks['inferencingOnlyPower'] else print("[No inferencing only Power selected]") 



    




        


                



