

# CatapultV3_conduit.py : 
This should be used after you have selected the data from the ParseAll.py report. Feed the selected Power, Socwatch, and PCIe-only socwatch summary file paths as a list of dictionary objects (JSON format). It will combine the power, socwatch, and PCIe-only socwatch summaries for the conduit data collateral. CPU P-states will be presented per core as requested by the projection team. You can hide (collapse) the 2nd to last cores in the unhighlighted past progression data to make the baseline and last progression data stand out more.

##### [Powershell example]
```powershell

PS C:\Users\siwoopar\code\ParseCSV> py CatapultV3_conduit.py -o .\test\2nd_folders (optional : -i \\255.255.255.255\Pnpext\Siwoo\data\WW2526.5_CataV3_IT_CCA_LC\Baseline\some.json)

```
### Arguments
##### -i, --input : You can omit it if you directly feed it in the CatapultV3_conduit.py as "SWP" dictionary. Or full path to input .JSON file that has "data_label", "condition", "data_summary_type", "power_summary_path", "socwatch_summary_path", and "PCIe_socwatch_summary_path"
##### -o, --output : full path to the output excel file location and filename prefix. "_allPower_v.xlsx" will be added in the file name.



```python
# OR direct feed in the CatapultV3_conduit.py (direct file path feed is easier [\\ issue] with python raw string option "r")
SWP = [
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
    },
]

```
[BACK](../)
