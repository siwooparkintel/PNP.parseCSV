import os
from pathlib import Path
import parsers.tools as tools
import parsers.ETLFirstEventParserByPS as ETLF


def filetime_to_epoch(filetime):
    """
    Convert Windows FILETIME to Unix Epoch timestamp
    Args:
        filetime (int): Windows FILETIME (100-nanosecond intervals since Jan 1, 1601)
    Returns:
        float: Unix timestamp (seconds since Jan 1, 1970)
    """
    # FILETIME epoch: January 1, 1601
    # Unix epoch: January 1, 1970  
    # Difference: 11644473600 seconds = 116444736000000000 * 100ns intervals
    
    FILETIME_EPOCH_DIFF = 116444736000000000
    FILETIME_TO_MILLISECONDS = 10000  # 100-nanosecond intervals per millisecond
    
    return (filetime - FILETIME_EPOCH_DIFF) / FILETIME_TO_MILLISECONDS







def parseETL(etl_path) :
    
    data = {}

    extractor = ETLF.ETLHighPrecisionTimeExtractor()
    
    # BASE = os.getcwd() #'C:\\Users\\siwoopar\\code\\parseCSV'
    # etl_file = os.path.join(BASE, "\\test\\web_cataV3ff_si.etl")

    try:
        #Get all timestamp formats
        timestamp_dict = extractor.get_first_event_times(etl_path)
        
        if timestamp_dict:
            print("First Event Timestamps:")
            print(f"Original DateTime: {timestamp_dict['datetime_original']}")
            print(f"FILETIME: {timestamp_dict['filetime']}")
            print(f"Unix Epoch (milliseconds): {timestamp_dict['epoch_milliseconds']}")

        
        # Or get just FILETIME (faster)
        # filetime = extractor.get_filetime_only(etl_file)
        # print(f"\nFILETIME only: {filetime}")
        
    except Exception as e:
        print(f"Error: {e}")

    data.update(timestamp_dict)
    return data
        


