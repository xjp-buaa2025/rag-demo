"""
generate_test_bom.py — 生成航空发动机测试 BOM 表

运行：
    python data/generate_test_bom.py

输出：
    data/test_bom.xlsx
"""

import os
import pandas as pd

# ── BOM 数据（模拟某型涡扇发动机，仅供测试）──────────────────────────────────
# 列定义：
#   level_code  : 层级编号（1 / 1.1 / 1.1.1 …）
#   part_id     : 零件编号（唯一）
#   part_name   : 零件名称（中文）
#   part_name_en: 零件名称（英文）
#   category    : Assembly（组件）/ Part（零件）/ Standard（标准件）
#   qty         : 数量
#   unit        : 单位
#   material    : 材料牌号（零件有值，组件为空）
#   weight_kg   : 重量 kg（估算）
#   spec        : 规格说明
#   note        : 备注

ROWS = [
    # level  part_id       part_name           part_name_en                         category    qty  unit  material          weight  spec                      note
    ("1",      "ENG-001",  "涡扇发动机整机",   "Turbofan Engine Assembly",          "Assembly",   1, "台",  "",               2800.0, "推力等级：150 kN",        "整机组装"),
    ("1.1",    "FAN-000",  "风扇模块",          "Fan Module",                        "Assembly",   1, "套",  "",                420.0, "",                        ""),
    ("1.1.1",  "FAN-D01",  "风扇盘",            "Fan Disk",                          "Part",       1, "件",  "TC4(Ti-6Al-4V)",   85.0, "φ1200×180 mm",           "锻件，需超声波探伤"),
    ("1.1.2",  "FAN-B01",  "风扇叶片",          "Fan Blade",                         "Part",      18, "件",  "Ti-6Al-4V",         3.2, "展弦比 3.5，弦长 180 mm", "带阻尼台，成对平衡"),
    ("1.1.3",  "FAN-S01",  "进气道导流叶片",    "Inlet Guide Vane",                  "Part",      36, "件",  "TC11",              0.8, "可调角度 ±15°",           ""),
    ("1.1.4",  "FAN-C01",  "前锥体",            "Spinner Cone",                      "Part",       1, "件",  "铝合金 2A12",       4.5, "φ400×600 mm",            ""),
    ("1.1.5",  "FAN-R01",  "风扇机匣",          "Fan Case",                          "Part",       1, "件",  "铝合金 2A14",      38.0, "φ1250×350 mm",           "带吸声衬套"),

    ("1.2",    "HPC-000",  "高压压气机模块",    "High-Pressure Compressor Module",   "Assembly",   1, "套",  "",                310.0, "9级轴流式",               ""),
    ("1.2.1",  "HPC-R01",  "高压压气机转子",    "HPC Rotor",                         "Assembly",   1, "套",  "",                180.0, "",                        ""),
    ("1.2.1.1","HPC-D01",  "1级压气机盘",       "HPC Stage-1 Disk",                  "Part",       1, "件",  "GH4169",           22.0, "φ560×90 mm",             "镍基高温合金"),
    ("1.2.1.2","HPC-B01",  "1级压气机叶片",     "HPC Stage-1 Blade",                 "Part",      32, "件",  "TC11",              0.35, "叶高 85 mm",             "燕尾形榫头"),
    ("1.2.1.3","HPC-D09",  "9级压气机盘",       "HPC Stage-9 Disk",                  "Part",       1, "件",  "GH4169",           28.0, "φ480×100 mm",            ""),
    ("1.2.1.4","HPC-B09",  "9级压气机叶片",     "HPC Stage-9 Blade",                 "Part",      56, "件",  "GH4033",            0.12, "叶高 32 mm",             ""),
    ("1.2.2",  "HPC-S01",  "高压压气机静子",    "HPC Stator",                        "Assembly",   1, "套",  "",                130.0, "",                        ""),
    ("1.2.2.1","HPC-V01",  "可调静子叶片",      "Variable Stator Vane",              "Part",      32, "件",  "TC6",               0.18, "前三级可调",             "带调节环"),
    ("1.2.2.2","HPC-C01",  "压气机机匣",        "HPC Casing",                        "Part",       1, "件",  "GH4169",           55.0, "φ500×680 mm",            "水平剖分"),

    ("1.3",    "CMB-000",  "燃烧室模块",        "Combustor Module",                  "Assembly",   1, "套",  "",                180.0, "环形燃烧室",              ""),
    ("1.3.1",  "CMB-O01",  "外机匣",            "Outer Combustor Casing",            "Part",       1, "件",  "GH4169",           32.0, "φ510×320 mm",            ""),
    ("1.3.2",  "CMB-I01",  "内机匣",            "Inner Combustor Casing",            "Part",       1, "件",  "GH4169",           18.0, "φ380×320 mm",            ""),
    ("1.3.3",  "CMB-L01",  "火焰筒",            "Combustion Liner",                  "Part",       1, "件",  "DZ125（定向凝固）", 22.0, "φ440×300 mm",           "发散冷却孔 φ0.5 mm，共 3200 个"),
    ("1.3.4",  "CMB-N01",  "燃油喷嘴",          "Fuel Nozzle",                       "Part",      24, "件",  "1Cr18Ni9Ti",        0.45, "双油路离心式",           "流量偏差 ≤3%"),
    ("1.3.5",  "CMB-I02",  "点火器",            "Igniter",                           "Standard",   2, "件",  "",                  0.12, "高能点火，30 J",         ""),

    ("1.4",    "HPT-000",  "高压涡轮模块",      "High-Pressure Turbine Module",      "Assembly",   1, "套",  "",                220.0, "单级轴流",                ""),
    ("1.4.1",  "HPT-N01",  "高压涡轮导向器",    "HPT Nozzle Guide Vane",             "Assembly",   1, "套",  "",                 45.0, "气膜冷却",                ""),
    ("1.4.1.1","HPT-V01",  "导向叶片",          "Nozzle Vane",                       "Part",      32, "件",  "DD6（单晶）",       0.28, "叶高 55 mm，带热障涂层", "真空精铸，5 层气膜孔"),
    ("1.4.2",  "HPT-R01",  "高压涡轮转子",      "HPT Rotor",                         "Assembly",   1, "套",  "",                 95.0, "",                        ""),
    ("1.4.2.1","HPT-D01",  "涡轮盘",            "Turbine Disk",                      "Part",       1, "件",  "GH4169",           42.0, "φ520×120 mm",            "粉末冶金盘，需荧光检测"),
    ("1.4.2.2","HPT-B01",  "涡轮工作叶片",      "HPT Rotor Blade",                   "Part",      80, "件",  "DD3（单晶）",       0.18, "带冠，内腔气冷",          "精铸，壁厚 0.5±0.05 mm"),
    ("1.4.2.3","HPT-S01",  "蓖齿封严环",        "Labyrinth Seal Ring",               "Part",       2, "件",  "GH4033",            3.2, "φ380×25 mm",             ""),

    ("1.5",    "LPT-000",  "低压涡轮模块",      "Low-Pressure Turbine Module",       "Assembly",   1, "套",  "",                280.0, "4级轴流",                 ""),
    ("1.5.1",  "LPT-N01",  "低压涡轮导向器",    "LPT Nozzle Guide Vane",             "Part",      48, "件",  "K438（铸造高温合金）",0.42, "气膜冷却，带热障涂层",   ""),
    ("1.5.2",  "LPT-R01",  "低压涡轮转子",      "LPT Rotor",                         "Assembly",   1, "套",  "",                165.0, "4级，带长轴",             ""),
    ("1.5.2.1","LPT-D01",  "1级低压涡轮盘",     "LPT Stage-1 Disk",                  "Part",       1, "件",  "GH4169",           38.0, "φ600×110 mm",            ""),
    ("1.5.2.2","LPT-B01",  "1级低压涡轮叶片",   "LPT Stage-1 Blade",                 "Part",      60, "件",  "K417G",             0.62, "叶高 120 mm，无冠",       ""),
    ("1.5.2.3","LPT-SH1",  "低压涡轮轴",        "LPT Shaft",                         "Part",       1, "件",  "40CrNiMoA",        28.0, "φ180×1400 mm",           "空心轴，内通冷却气"),

    ("1.6",    "ACS-000",  "附件传动系统",      "Accessory Drive System",            "Assembly",   1, "套",  "",                 95.0, "",                        ""),
    ("1.6.1",  "ACS-G01",  "附件齿轮箱",        "Accessory Gearbox",                 "Assembly",   1, "套",  "",                 48.0, "锥齿轮传动",              ""),
    ("1.6.1.1","ACS-G11",  "传动锥齿轮",        "Bevel Drive Gear",                  "Part",       3, "件",  "12Cr2Ni4A",         2.8, "模数 4，齿数 32",        "渗碳淬火"),
    ("1.6.1.2","ACS-GB1",  "齿轮箱壳体",        "Gearbox Housing",                   "Part",       1, "件",  "ZL101A（铸铝）",   12.0, "",                        ""),
    ("1.6.2",  "OIL-000",  "滑油系统",          "Lubrication System",                "Assembly",   1, "套",  "",                 22.0, "",                        ""),
    ("1.6.2.1","OIL-P01",  "滑油泵",            "Oil Pump",                          "Part",       1, "件",  "40Cr",              3.5, "齿轮泵，流量 40 L/min",  ""),
    ("1.6.2.2","OIL-F01",  "滑油过滤器",        "Oil Filter",                        "Standard",   2, "件",  "",                  0.8, "过滤精度 40 μm",         ""),
    ("1.6.3",  "FCU-001",  "燃油调节器",        "Fuel Control Unit (FCU)",           "Part",       1, "件",  "",                  6.5, "全权数字电调（FADEC）",   "外购件"),

    ("1.7",    "NOZ-000",  "尾喷管模块",        "Exhaust Nozzle Module",             "Assembly",   1, "套",  "",                 85.0, "收敛-扩散可调喷管",       ""),
    ("1.7.1",  "NOZ-C01",  "收敛段",            "Convergent Section",                "Part",       1, "件",  "GH4169",           22.0, "最小截面φ320 mm",        "隔热毯覆盖"),
    ("1.7.2",  "NOZ-D01",  "扩散段",            "Divergent Flap Assembly",           "Part",      16, "件",  "GH1015",            3.2, "可调，±30°",             ""),
    ("1.7.3",  "NOZ-A01",  "作动筒",            "Actuator",                          "Standard",   8, "件",  "",                  1.8, "液压驱动，行程 80 mm",   ""),
]

COLUMNS = ["level_code", "part_id", "part_name", "part_name_en",
           "category", "qty", "unit", "material", "weight_kg", "spec", "note"]

df = pd.DataFrame(ROWS, columns=COLUMNS)

out_path = os.path.join(os.path.dirname(__file__), "test_bom.xlsx")
df.to_excel(out_path, index=False, sheet_name="BOM")
print(f"已生成 BOM 表：{out_path}（共 {len(df)} 行）")
