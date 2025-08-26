

# ParseAll.py : 
This is developed to parse and summarize all ETL/Power/Socwatch/PCIe_Only data into one Excel file to help with the data selection process. Power comes first; if the power data is collected with Socwatch or PCIe-only Socwatch, they will be parsed and presented in one column. Currently, ETL is not being post-processed.



### Arguments
##### -i, --input : full path to the folder
##### -o, --output : full path to the output excel file location and filename prefix. "_allPower_v.xlsx" will be added in the file name.
##### [Powershell example]
```powershell

PS C:\Users\siwoopar\code\ParseCSV> py ParseAll.py -i \\255.255.255.255\Pnpext\Siwoo\data\WW2526.5_CataV3_IT_CCA_LC\Baseline -o .\test\2nd_folders

```

### Acceptable Folder Structures
-----------------------------------------------------------------------------------------------------------------------------------------
##### [Folder Structure 1 (flat layer)]

It requires to provide upto "Baseline" folder as a input and children folders are a flat level. each folder can be, ETL, Power, PCIe, or Socwatch
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

need to provide upto "Baseline" folder as a input and children folders can be grouped as ETL, Power, Socwatch or PCIe
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



[BACK](../README.md)