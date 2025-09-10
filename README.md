# Parsers / Summarizers

## For General Users
[Workload_Parser](./Workload_Parser/) : This is integrated version, including all small Python tools, ex) ParserAll.py and Collection_Parser.py. Other workload specific parser will be added here. so please use this tool group for general usage.

#### Tool BKM
=> [Tool BKM](./Workload_Parser/tool_BKM.md)

------------------------------------------------------------------------

## For CPAD team (P3TMA)

[ParseAll.py](./ParseAll/) : This is developed to parse and summarize all ETL/Power/Socwatch/PCIe_Only data into one Excel file to help with the data selection process. Power comes first; if the power data is collected with Socwatch or PCIe-only Socwatch, they will be parsed and presented in one column. Currently, ETL is not being post-processed.

[CatapultV3_conduit.py](./CatapultV3_conduit/) : This should be used after you have selected the data from the ParseAll.py report. Feed the selected Power, Socwatch, and PCIe-only socwatch summary file paths as a list of dictionary objects (JSON format). It will combine the power, socwatch, and PCIe-only socwatch summaries for the conduit data collateral. CPU P-states will be presented per core as requested by the projection team. You can hide (collapse) the 2nd to last cores in the unhighlighted past progression data to make the baseline and last progression data stand out more.

------------------------------------------------------------------------

## For AI Workload (NPU/GPU Integration Team)

AI_Summary2 (Pandas + openpyxl): detect every file and folder in the target path, parse Power, ETL, AI Model throughput results, and Socwatch into one summary Excel (openpyxl). it is designed for huge dataset like running 50+ AI models on GPU and NPU and summaries the result.
    ex) C:\User\yourfolder>py parsing_AI_summary.py -i \\255.255.255.255\yourdatalocatio\ -o(-output optional) \\255.255.255.255\yourdatalocatio\summary_file_name

AI_Summary (older version, no need Pandas) : detect every file and folder in the target path, parse Power, ETL, AI Model throughput results, and Socwatch into one summary CSV (later Excel). it is designed for huge dataset like running 50+ AI models on GPU and NPU and summaries the result.
    ex) C:\User\yourfolder>py parsing_AI_summary.py -i \\255.255.255.255\yourdatalocatio\ -o(-output optional) \\255.255.255.255\yourdatalocatio\summary_file_name

------------------------------------------------------------------------

## Other Parsers

PowerSocPCIe_summary : this summarizer is for Client Platform Architect Team's collateral data support. for now data selection process need to be done by manual. providing list of dictionaries of following example. "data_label" must be unique. PCIe_socwatch need to be collected with only -f PCIe flag which should have minimal power impact. if you don't provide "PCIe_socwatch_summary_path" it will be skipped.

```python
    {
        "data_label":"CataV3+IT+CCA+LCLT+UHX2",
        "power_summary_path":r"your\data\location",
        "socwatch_summary_path":r"your\data\location",
        "PCIe_socwatch_summary_path":r"your\data\location"
    },
```

parseText : parsing Text results to generate CSV summary

sliceSocwatch : using filled CSV time table, slice existing socwatch data to create subsection of the socwatch socwatch 2025.1 or higher recommended

