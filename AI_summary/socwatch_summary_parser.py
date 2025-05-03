
"""
Socwatch Options:
Command line options: -s 0 -o c:\hobl_data\socwatch\AI_GPU_model_stripped -f temp -f npu -f gfx -f memss-pstate -f cpu-cstate -f hw-cpu-hwp -f hw-cpu-cstate -f hw-cpu-pstate -f os-cpu-cstate -f os-cpu-pstate -f hw-igfx-cstate -f hw-igfx-pstate -f display-state -f ddr-bw -f bw-all -f noc-pstate -f media-pstate -m -r auto --no-post-processing 
"""

socwatch_targets = [
    {"key": "pkg_cstate", "lookup": "Platform Monitoring Technology CPU Package C-States Residency Summary: Residency (Percentage and Time)"},
    {"key": "core_cstate", "lookup": "Core C-State Summary: Residency (Percentage and Time)"},
    {"key": "acpi_cstate", "lookup": "Core C-State (OS) Summary: Residency (Percentage and Time)"},
    {"key": "os_wakeups", "lookup": "Processes by Platform Busy Duration"},
    {"key": "cpu_pstate", "lookup": "CPU P-State Average Frequency (excluding CPU idle time)"},
    {"key": "cpu_freq", "lookup": "CPU P-State/Frequency Summary: Residency (Percentage and Time)"},
    {"key": "rc_cstate", "lookup": "Integrated Graphics C-State  Summary: Residency (Percentage and Time)"},
    {"key": "ddr_bw", "lookup": "DDR Bandwidth Requests by Component Summary: Average Rate and Total"},
    {"key": "io_bw", "lookup": "IO Bandwidth Summary: Average Rate and Total"},
    {"key": "vc1_bw", "lookup": "Display VC1 Bandwidth Summary: Average Rate and Total"},
    {"key": "npu_bw", "lookup": "Neural Processing Unit (NPU) to Memory Bandwidth Summary: Average Rate and Total"},
    {"key": "media_bw", "lookup": "Media to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "ipu_bw", "lookup": "Image Processing Unit (IPU) to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "cce_bw", "lookup": "CCE to Network on Chip (NoC) Bandwidth Summary: Average Rate and Total"},
    {"key": "gt_bw", "lookup": "Network on a Chip GT Bandwidth Summary: Average Rate and Total"},
    {"key": "cpu_temp", "lookup": "Temperature Metrics Summary - Sampled: Min/Max/Avg"},
    {"key": "soc_temp", "lookup": "SoC Domain Temperatures Summary - Sampled: Min/Max/Avg"},
    {"key": "npu_dstate", "lookup": "Neural Processing Unit (NPU) D-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "dc_count", "lookup": "Dynamic Display State Enabling"},
    {"key": "media_cstate", "lookup": "Media C-State Residency Summary: Residency (Percentage and Time)"},
    {"key": "npu_pstate", "lookup": "Neural Processing Unit (NPU) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "memss_pstate", "lookup": "Memory Subsystem (MEMSS) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "noc_pstate", "lookup": "Network on Chip (NoC) P-State Summary - Sampled: Approximated Residency (Percentage)"},
    {"key": "igfx_pstate", "lookup": "Integrated Graphics P-State/Frequency Summary - Sampled: Approximated Residency (Percentage)"}
]

"""


"""





def parseSocwatch(abs_path) :

    socwatch_obj = dict()
    socwatch_obj['socwatch_path'] = abs_path
    socwatch_obj['socwatch_tables'] = []

    with open(abs_path, 'r') as file:


        for target in socwatch_targets : 
            tTable = dict()
            for line in file :
                tline = line.strip()
                if 'isOpen' in tTable and tTable['isOpen'] == True :
                    if tline == "" :
                        tTable['isOpen'] = False
                        socwatch_obj['socwatch_tables'].append(tTable)
                        break
                    else :
                        tTable['table_data'].append([item.strip() for item in tline.split(',')])
                elif tline.rfind(target['lookup']) >=0 :
                    tTable['label'] = target['key']
                    tTable['table_data'] = list()
                    tTable['isOpen'] = True  



        
        # print("[SI] ====================", socwatch_obj)

        return socwatch_obj
    
