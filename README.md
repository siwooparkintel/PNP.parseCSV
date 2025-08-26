# Parsers / Summarizers
## for CPAD team (P3TMA)

[ParseAll.py](./ParseAll/ParseAll.md) : This is developed to parse and summarize all ETL/Power/Socwatch/PCIe_Only data into one excel, to help the data selection process. Power comes first, if the power data collected with Socwatch or PCIe_only Socwatch, they will be parsed and presented in one column. currently ETL is not being post-processed. 

[CatapultV3_conduit.py](./CatapultV3_conduit/CatapultV3_conduit.md) : this should be used after you pick and choose the data from the ParseAll.py. Feed the selected Power, Socwatch, PCIe_Only file paths as a list of dictionary object(JSON format), it will combine the power and socwatch and PCIe_only for the conduit data upload. CPU P-states will be presented per core as the projection team requested. you can hide (collapse) the 2nd to last cores on the unhighlighted past progressed data to make the baseline and last progression data more stands out.  

------------------------------------------------------------------------

# Other Parsers
AI_Summary2 (Pandas + openpyxl): detect every file and folder in the target path, parse Power, ETL, AI Model throughput results, and Socwatch into one summary Excel (openpyxl). it is designed for huge dataset like running 50+ AI models on GPU and NPU and summaries the result.
    ex) C:\User\yourfolder>py parsing_AI_summary.py -i \\255.255.255.255\yourdatalocatio\ -o(-output optional) \\255.255.255.255\yourdatalocatio\summary_file_name

AI_Summary (older version, no need Pandas) : detect every file and folder in the target path, parse Power, ETL, AI Model throughput results, and Socwatch into one summary CSV (later Excel). it is designed for huge dataset like running 50+ AI models on GPU and NPU and summaries the result.
    ex) C:\User\yourfolder>py parsing_AI_summary.py -i \\255.255.255.255\yourdatalocatio\ -o(-output optional) \\255.255.255.255\yourdatalocatio\summary_file_name

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

