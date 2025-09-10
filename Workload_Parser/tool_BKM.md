
# BKM : 

### 0. Prerequisite
#### (1) Install Python [Python Download](https://www.python.org/downloads/)
#### (2) Install VS Code [VS Code Download(System,x64 on Windows)](https://code.visualstudio.com/download)
#### (3) Install Git [GIT Download](https://git-scm.com/downloads/win)
#### (4) Signup for Github [Github Signup](https://github.com/) 

Recommend to download Windows/x64 Setup if you are on a Intel/Windows System.
Install all downloaded installers. During the installation, default section will be good enough but recommend to choose "VS code" as GIT editor instead of VIM.
Signup for Github to download the codebase.


-----------------------------------------------------------------------------------------------------------------------------------------


### 1. Clone the code from Github
```powershell

PS C:\Users\YOURNAME\code>git clone https://github.com/siwooparkintel/PNP.parseCSV.git

Cloning into 'PNP.parseCSV'...
remote: Enumerating objects: 445, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (4/4), done.
Receie: Total 445 (delta 0), reused 1 (delta 0), pack-reused 441 (from 1)R             cts:  95% (423/445)
Receiving objects: 100% (445/445), 286.01 KiB | 1.55 MiB/s, done.
Resolving deltas: 100% (258/258), done.

```

# Workload_Parser Folder
## Among the many, "Workload_Parser" is the one folder that all small parsers are integrated, including "ParseAll.py" and "Collection_Parser.py"









# ParseAll.py : 
This is developed to parse and summarize all ETL/Power/Socwatch/PCIe_Only data into one Excel file to help with the data selection process. Power comes first; if the power data is collected with Socwatch or PCIe-only Socwatch, they will be parsed and presented in one column. Currently, ETL is not being post-processed.

##### [Powershell example]
```powershell

PS C:\Users\YOURNAME\ParseCSV\Workload_Parser> py ParseAll.py -i \\255.255.255.255\Pnpext\Siwoo\data\WW2526.5_CataV3_IT_CCA_LC\Baseline -o .\test\2nd_folders -d .\src\DAQ_target_LNL09-04DUT.json -st .\src\Socwatch_targets.json

```

### Acceptable Folder Structures
-----------------------------------------------------------------------------------------------------------------------------------------
##### [Folder Structure 1 (flat layer)]

It requires to provide upto "Baseline" (or different name) folder as a input  and children folders are a flat level. each folder can be, ETL, Power, PCIe, or Socwatch
<pre>
WW2534.1_somedata ├── Baseline ├── CataV3_000 (ETL + Power)
                               ├── CataV3_001 (Power)
                               ├── CataV3_002 (Power)
                               ├── CataV3_003 (Power)
                               ├── CataV3_004 (Socwatch + Power)
                               ├── CataV3_005 (Socwatch + Power)
                               ├── CataV3_006 (Socwatch + Power)
                               ├── CataV3_007 (PCIe Only Socwatch + Power)
                               └── CataV3_008 (PCIe Only Socwatch + Power)
</pre>
##### [Folder Structure 2 (2 layers)]

It requires to provide upto "Baseline" (or different name) folder as a input and children folders can be grouped as ETL, Power, Socwatch or PCIe (exact folder names are needed here)
<pre>
WW2534.1_somedata ├── Baseline  ├── ETL          └── CataV3_000 (ETL + Power)
                                ├── Power        ├── CataV3_001 (Power)
                                │                ├── CataV3_002 (Power)
                                │                └── CataV3_003 (Power)
                                ├── Socwatch     ├── CataV3_004 (Socwatch + Power)
                                │                ├── CataV3_005 (Socwatch + Power)
                                │                └── CataV3_006 (Socwatch + Power)
                                └── PCIe         ├── CataV3_007 (PCIe Only Socwatch + Power)
                                                 └── CataV3_008 (PCIe Only Socwatch + Power)
</pre>

### Arguments
##### -i, --input [required] : full path to the folder
##### -o, --output [recommended]: full path to the output excel file location and filename prefix. "_allPower_v.xlsx" will be added in the file name.
##### -d, --daq [recommended]: full path and json file name. it externalizes the DAQ_target dictionary object as a json since each DAQ can have different power measure rail names.
##### -st, --swtarget [optional]: full path and json file name that contains a list of dictionary object that contains "look up" text in the socwatch summary file to parse. if the dictionary has "buckets" list it will bucketize the p-states into defined range group.
##### -hb, --hobl [optional]: If data is collected through HOBL, it should have .PASS or .FAIL empty file, and using them to set a data group is much more accurate, so recommended to use it if it is collected via HOBL. 


### DAQ Rail Name Adjustment (-d, --daq)

Each DAQ power rail name can be different. To summarize the targeted rails, modify the "DAQ_target" object in ParseAll.py or provide the -d flag with the full path and JSON file name. Lastly if you add "Rum Time" in the DAQ_target, it will provide the total energy (J) used during the workload.

```python

DAQ_target = {
"P_SSD":-1,
"V_VAL_VCC_PCORE":-1,
"I_VAL_VCC_PCORE":-1,
"V_VAL_VCC_ECORE":-1,
"I_VAL_VCC_ECORE":-1,
"V_VAL_VCCSA":-1,
"I_VAL_VCCSA":-1,
"V_VAL_VCCGT":-1,
"I_VAL_VCCGT":-1,
"P_VCC_PCORE":-1,
"P_VCC_ECORE":-1,
"P_VCCSA":-1,
"P_VCCGT":-1,
"P_VCCL2":-1,
"P_VCC1P8":-1,
"P_VCCIO":-1,
"P_VCCDDRIO":-1,
"P_VNNAON":-1,
"P_VNNAONLV":-1,
"P_VDDQ":-1,
"P_VDD2H":-1,
"P_VDD2L":-1,
"P_V1P8U_MEM":-1,
"P_SOC+MEMORY":-1,
"Run Time":-1
}

```

### Socwatch Target Table List Adjustment (-st, --swtarget)

If it is not provided, it uses an internally implemented target object, which works well. However, detection wording changes are possible by Socwatch developers. A user can add or remove the targeted socwatch summary table data here; bucketizing a large range of p-states is also possible. One important thing to get the best performance out of the parser is to match the order of the socwatch summary. If it is matched, it only loops once and parses every table together in that one loop. However, if not matched, it wastes the loop and loops again to check its existence.

```python

socwatch_targets = [
    {"key": "CPU_model", "lookup": "CPU native model"},
    {"key": "PCH_SLP50", "lookup": "PCH SLP-S0 State Summary: Residency (Percentage and Time)"},
    {"key": "S0ix_Substate", "lookup": "S0ix Substate Summary: Residency (Percentage and Time)"},
    {"key": "PKG_Cstate", "lookup": "Platform Monitoring Technology CPU Package C-States Residency Summary: Residency (Percentage and Time)"},
    {"key": "Core_Cstate", "lookup": "Core C-State Summary: Residency (Percentage and Time)"},
    {"key": "Core_Concurrency", "lookup": "CPU Core Concurrency (OS)"},
    {"key": "ACPI_Cstate", "lookup": "Core C-State (OS) Summary: Residency (Percentage and Time)"},
    {"key": "OS_wakeups", "lookup": "Processes by Platform Busy Duration"},
    {"key": "CPU-iGPU", "lookup": "CPU-iGPU Concurrency Summary: Residency (Percentage and Time)"},
    {"key": "CPU_Pavr", "lookup": "CPU P-State Average Frequency (excluding CPU idle time)"},
    {"key": "CPU_Pstate", "lookup": "CPU P-State/Frequency Summary: Residency (Percentage and Time)"},
    {"key": "RC_Cstate", "lookup": "Integrated Graphics C-State  Summary: Residency (Percentage and Time)"},
    {"key": "DDR_BW", "lookup": "DDR Bandwidth Requests by Component Summary: Average Rate and Total"},
    {"key": "IO_BW", "lookup": "IO Bandwidth Summary: Average Rate and Total"},
    {"key": "VC1_BW", "lookup": "Display VC1 Bandwidth Summary: Average Rate and Total"},
    {"key": "NPU_BW", "lookup": "Neural Processing Unit (NPU) to Memory Bandwidth Summary: Average Rate and Total"},
    {"key": "Media_BW", "lookup": "Media to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "IPU_BW", "lookup": "Image Processing Unit (IPU) to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "CCE_BW", "lookup": "CCE to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "GT_BW", "lookup": "Chip GT Bandwidth Summary: Average Rate and Total"},
    {"key": "D2D_BW", "lookup": "Chip Die to Die Bandwidth Summary: Average Rate and Total"},
    {"key": "CPU_temp", "lookup": "Temperature Metrics Summary - Sampled: Min/Max/Avg"},
    {"key": "SoC_temp", "lookup": "SoC Domain Temperatures Summary - Sampled: Min/Max/Avg"},
    {"key": "NPU_Dstate", "lookup": "Neural Processing Unit (NPU) D-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "PMC+SLP_S0", "lookup": "PCH Active State (as percentage of PMC Active plus SLP_S0 Time) Summary: Residency (Percentage)"},
    {"key": "DC_count", "lookup": "Dynamic Display State Enabling"},
    {"key": "Media_Cstate", "lookup": "Media C-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "NPU_Pstate", "lookup": "Neural Processing Unit (NPU) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "1900", "1901-2900", "2901-3899", "3900"]},
    {"key": "MEMSS_Pstate", "lookup": "Memory Subsystem (MEMSS) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "NoC_Pstate", "lookup": "Network on Chip (NoC) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["400", "401-1049", "1050"]},
    {"key": "iGFX_Pstate", "lookup": "Integrated Graphics P-State/Frequency Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "400", "401-1799", "1800-2049", "2050"]}
]

```

### HOBL or Non-HOBL data (-hb, --hobl)
If the data is collected via HOBL, using this option to improve the data detection. It is empty flag, add it if it is hobl data or omit it if not.




=======================================================================================================================================



# Collection_Parser.py : 
This should be used after you have selected the data from the ParseAll.py report. Feed the selected Power, Socwatch, and PCIe-only socwatch summary file paths as a list of dictionary objects (JSON format). It will combine the power, socwatch, and PCIe-only socwatch summaries for the conduit data collateral. CPU P-states will be presented per core as requested by the projection team. You can hide (collapse) the 2nd to last cores in the unhighlighted past progression data to make the baseline and last progression data stand out more.

##### [Powershell example]
```powershell

PS C:\Users\YOURNAME\ParseCSV\Workload_Parser> py Collection_Parser.py -i .\src\collection.json -o .\test\2nd_file_prefix -d .\src\DAQ_target_LNL09-04DUT.json -st .\src\Socwatch_targets.json

```
### Arguments
##### -i, --input [optional] : You can omit it if you directly feed it in the Collection_Parser.py as "collection" dictionary. Or full path to input .JSON file that has "data_label", "condition", "data_summary_type", "power_summary_path", "socwatch_summary_path", and "PCIe_socwatch_summary_path"
##### -o, --output [recommended] : full path to the output excel file location and filename prefix. "_allPower_v.xlsx" will be added in the file name.
##### -d, --daq [recommended]: full path and json file name. it externalizes the DAQ_target dictionary object as a json since each DAQ can have different power measure rail names.
##### -st, --swtarget [optional]: full path and json file name that contains a list of dictionary object that contains "look up" text in the socwatch summary file to parse. if the dictionary has "buckets" list it will bucketize the p-states into defined range group.


### Collection of Selected Data (-i, --input)

After completing the data selection process, a user can directly modify the "collection", a list of dictionaries that contains grouped collateral. The benefit of directly feeding into Collection_Parser.py is that a user can avoid the Windows file path "escape " problem by using "r" in front of the string value. Users also can use JSON format data feed with the -i or --input option; in this case, hardcoded collection in the Collection_Parser.py will be ignored. 

#### About "data_summary_type"
If it is "compact" the 2nd to last core P-state will be hidden or collapsed, if it is "expanded" all core's P-state will be visible in the vertical "_v.xlsx" excel file.

```python
# OR direct feed in the Collection_Parser.py (direct file path feed is easier [\\ issue] with python raw string option "r")
collection = [
    {
        "data_label":"CataV3 UHX1",
        "condition":"CataV3+UHX1",
        "data_summary_type": "compact",
        "power_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW20.2_LNL32_CataV3_PC10.2\PC10.2_UHX\web_cataV3_si_001_ppick\web_cataV3_si_001\web_cataV3_si_001_pacs-summary.csv",
        "socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW20.2_LNL32_CataV3_PC10.2\PC10.2_UHX\web_cataV3_si_008_spick\socwatch\PC10.2_UHX_web_cataV3_si.csv",
        "PCIe_socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW20.2_LNL32_CataV3_PC10.2\PCIe_only_Socwatch\UHX_baseline\web_cataV3_si_002_pick\socwatch\web_cataV3_si_CataV3_UHX.csv"
    },    
    {
        "data_label":"CataV3 UHX1 LC",
        "condition":"CataV3+UHX1+LC",
        "data_summary_type": "compact",
        "power_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW20.2_LNL32_CataV3_PC10.2\PC10.2_UHX_LCLT\web_cataV3_si_006_ppick\web_cataV3_si_006\web_cataV3_si_006_pacs-summary.csv",
        "socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW20.2_LNL32_CataV3_PC10.2\PC10.2_UHX_LCLT\web_cataV3_si_000_spick\socwatch\PC10.2_UHX_LCLT_web_cataV3_si.csv",
        "PCIe_socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW20.2_LNL32_CataV3_PC10.2\PCIe_only_Socwatch\UHX_LCLT\web_cataV3_si_000_pick\socwatch\web_cataV3_si_CataV3_UXH_LCLT.csv"
    },
    {
        "data_label":"CataV3 UHX2 baseline",
        "condition":"CataV3+IT+BG+UHX2_10s",
        "data_summary_type": "expanded",
        "power_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2533.2_CataV3ITCCAUHX2_DCBAL\UHX2_DC_011\UHX2_DC_011_pacs-summary.csv",
        "socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2534.1_CataV3ITCCAUHX2_L0MPHYL6\CataV3_PCDfix_002\socwatch\CataV3_002.csv",
        "PCIe_socwatch_summary_path":r"\\amr.corp.intel.com\EC\proj\pst\jf\SPA-Lab\Siwoo\CatapultV3\WW2534.1_CataV3ITCCAUHX2_L0MPHYL6\CataV3_PCDfix_004\socwatch\CataV3_004.csv"
    }
]

```

### DAQ Rail Name Adjustment (-d, --daq)

Each DAQ power rail name can be different. To summarize the targeted rails, modify the "DAQ_target" object in ParseAll.py or provide the -d flag with the full path and JSON file name. Lastly if you add "Rum Time" in the DAQ_target, it will provide the total energy (J) used during the workload.

```python

DAQ_target = {
"P_SSD":-1,
"V_VAL_VCC_PCORE":-1,
"I_VAL_VCC_PCORE":-1,
"V_VAL_VCC_ECORE":-1,
"I_VAL_VCC_ECORE":-1,
"V_VAL_VCCSA":-1,
"I_VAL_VCCSA":-1,
"V_VAL_VCCGT":-1,
"I_VAL_VCCGT":-1,
"P_VCC_PCORE":-1,
"P_VCC_ECORE":-1,
"P_VCCSA":-1,
"P_VCCGT":-1,
"P_VCCL2":-1,
"P_VCC1P8":-1,
"P_VCCIO":-1,
"P_VCCDDRIO":-1,
"P_VNNAON":-1,
"P_VNNAONLV":-1,
"P_VDDQ":-1,
"P_VDD2H":-1,
"P_VDD2L":-1,
"P_V1P8U_MEM":-1,
"P_SOC+MEMORY":-1,
"Run Time":-1
}

```

### Socwatch Target Table List Adjustment (-st, --swtarget)

If it is not provided, it uses an internally implemented target object, which works well. However, detection wording changes are possible by Socwatch developers. A user can add or remove the targeted socwatch summary table data here; bucketizing a large range of p-states is also possible. One important thing to get the best performance out of the parser is to match the order of the socwatch summary. If it is matched, it only loops once and parses every table together in that one loop. However, if not matched, it wastes the loop and loops again to check its existence.

```python

socwatch_targets = [
    {"key": "CPU_model", "lookup": "CPU native model"},
    {"key": "PCH_SLP50", "lookup": "PCH SLP-S0 State Summary: Residency (Percentage and Time)"},
    {"key": "S0ix_Substate", "lookup": "S0ix Substate Summary: Residency (Percentage and Time)"},
    {"key": "PKG_Cstate", "lookup": "Platform Monitoring Technology CPU Package C-States Residency Summary: Residency (Percentage and Time)"},
    {"key": "Core_Cstate", "lookup": "Core C-State Summary: Residency (Percentage and Time)"},
    {"key": "Core_Concurrency", "lookup": "CPU Core Concurrency (OS)"},
    {"key": "ACPI_Cstate", "lookup": "Core C-State (OS) Summary: Residency (Percentage and Time)"},
    {"key": "OS_wakeups", "lookup": "Processes by Platform Busy Duration"},
    {"key": "CPU-iGPU", "lookup": "CPU-iGPU Concurrency Summary: Residency (Percentage and Time)"},
    {"key": "CPU_Pavr", "lookup": "CPU P-State Average Frequency (excluding CPU idle time)"},
    {"key": "CPU_Pstate", "lookup": "CPU P-State/Frequency Summary: Residency (Percentage and Time)"},
    {"key": "RC_Cstate", "lookup": "Integrated Graphics C-State  Summary: Residency (Percentage and Time)"},
    {"key": "DDR_BW", "lookup": "DDR Bandwidth Requests by Component Summary: Average Rate and Total"},
    {"key": "IO_BW", "lookup": "IO Bandwidth Summary: Average Rate and Total"},
    {"key": "VC1_BW", "lookup": "Display VC1 Bandwidth Summary: Average Rate and Total"},
    {"key": "NPU_BW", "lookup": "Neural Processing Unit (NPU) to Memory Bandwidth Summary: Average Rate and Total"},
    {"key": "Media_BW", "lookup": "Media to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "IPU_BW", "lookup": "Image Processing Unit (IPU) to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "CCE_BW", "lookup": "CCE to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "GT_BW", "lookup": "Chip GT Bandwidth Summary: Average Rate and Total"},
    {"key": "D2D_BW", "lookup": "Chip Die to Die Bandwidth Summary: Average Rate and Total"},
    {"key": "CPU_temp", "lookup": "Temperature Metrics Summary - Sampled: Min/Max/Avg"},
    {"key": "SoC_temp", "lookup": "SoC Domain Temperatures Summary - Sampled: Min/Max/Avg"},
    {"key": "NPU_Dstate", "lookup": "Neural Processing Unit (NPU) D-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "PMC+SLP_S0", "lookup": "PCH Active State (as percentage of PMC Active plus SLP_S0 Time) Summary: Residency (Percentage)"},
    {"key": "DC_count", "lookup": "Dynamic Display State Enabling"},
    {"key": "Media_Cstate", "lookup": "Media C-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "NPU_Pstate", "lookup": "Neural Processing Unit (NPU) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "1900", "1901-2900", "2901-3899", "3900"]},
    {"key": "MEMSS_Pstate", "lookup": "Memory Subsystem (MEMSS) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "NoC_Pstate", "lookup": "Network on Chip (NoC) P-State Summary - Sampled: Approximated Residency (Percentage)", "buckets":["400", "401-1049", "1050"]},
    {"key": "iGFX_Pstate", "lookup": "Integrated Graphics P-State/Frequency Summary - Sampled: Approximated Residency (Percentage)", "buckets":["0", "400", "401-1799", "1800-2049", "2050"]}
]

```




[BACK](../)
