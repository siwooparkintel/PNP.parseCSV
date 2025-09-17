import parsers.reporter_allpower as rap
import parsers.reporter_inferenceOnly as rinf



def writeParsedSelectionInExcel(result_path, hobl_data, picks, socwatch_targets, PCIe_targets) :
    rap.reportAllPowerAndType2(result_path, hobl_data, picks, socwatch_targets, PCIe_targets)


def writeParsedAllInExcel(result_path, hobl_sets, socwatch_targets, PCIe_targets, picks) :
    rap.reportAllPowerAndType(result_path, hobl_sets, picks, socwatch_targets, PCIe_targets)

    
def writeInferenceOnlyInExcel(result_path, hobl_sets, DAQ_target) :
    rinf.reportInferencingOnlyPower(result_path, hobl_sets, DAQ_target)


