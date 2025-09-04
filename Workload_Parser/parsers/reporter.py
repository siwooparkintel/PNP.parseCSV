import parsers.reporter_allpower as rap



def writeParsedSelectionInExcel(result_path, hobl_data, picks, socwatch_targets, PCIe_targets) :
    rap.reportAllPowerAndType2(result_path, hobl_data, picks, socwatch_targets, PCIe_targets)


def writeParsedAllInExcel(result_path, hobl_sets, socwatch_targets, PCIe_targets, picks) :
    rap.reportAllPowerAndType(result_path, hobl_sets, picks, socwatch_targets, PCIe_targets)

    



