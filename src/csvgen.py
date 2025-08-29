import csv
import os
import glob
from datetime import datetime, timedelta
from typing import List, Dict
import logging

class CSVGenerator:
    # Mapping of raw sensor IDs to human-readable names
    SENSOR_NAME_MAPPINGS = {
        # Temperature sensors
        "calculations.ID_WEB_Temperatur_TVL": "Flow Temperature",
        "calculations.ID_WEB_Temperatur_TRL": "Return Temperature",
        "calculations.ID_WEB_Temperatur_TA": "Ambient Temperature",
        "calculations.ID_WEB_Temperatur_TBW": "Hot Water Temperature",
        "calculations.ID_WEB_Sollwert_TRL_HZ": "Return Temperature Setpoint Heating",
        "calculations.ID_WEB_Temperatur_TRL_ext": "Return Temperature External",
        "calculations.ID_WEB_Temperatur_THG": "Heat Source Temperature",
        "calculations.ID_WEB_Mitteltemperatur": "Average Temperature",
        "calculations.ID_WEB_Einst_BWS_akt": "Hot Water Setpoint",
        "calculations.ID_WEB_Temperatur_TWE": "Evaporator Temperature",
        "calculations.ID_WEB_Temperatur_TWA": "Condenser Temperature",
        "calculations.ID_WEB_Temperatur_TFB1": "Mixed Circuit 1 Flow Temperature",
        "calculations.ID_WEB_Sollwert_TVL_MK1": "Mixed Circuit 1 Flow Temperature Setpoint",
        "calculations.ID_WEB_Temperatur_RFV": "Room Flow Temperature",
        "calculations.ID_WEB_Temperatur_TFB2": "Mixed Circuit 2 Flow Temperature",
        "calculations.ID_WEB_Sollwert_TVL_MK2": "Mixed Circuit 2 Flow Temperature Setpoint",
        "calculations.ID_WEB_Temperatur_TSK": "Tank Temperature Top",
        "calculations.ID_WEB_Temperatur_TSS": "Tank Temperature Bottom",
        "calculations.ID_WEB_Temperatur_TEE": "Evaporation Temperature",
        "calculations.ID_WEB_LIN_ANSAUG_VERDAMPFER": "Suction Evaporator Temperature",
        "calculations.ID_WEB_LIN_ANSAUG_VERDICHTER": "Suction Compressor Temperature",
        "calculations.ID_WEB_LIN_VDH": "Superheating",
        "calculations.ID_WEB_LIN_UH": "Superheating Target",
        "calculations.ID_WEB_LIN_HD": "High Pressure",
        "calculations.ID_WEB_LIN_ND": "Low Pressure",
        "calculations.ID_WEB_LIN_ANSAUG_VERDAMPFER_2": "Suction Evaporator Temperature 2",
        "calculations.ID_WEB_LIN_ANSAUG_VERDICHTER_2": "Suction Compressor Temperature 2",
        "calculations.ID_WEB_LIN_VDH_2": "Superheating 2",
        "calculations.ID_WEB_LIN_UH_2": "Superheating Target 2",
        "calculations.ID_WEB_LIN_HD_2": "High Pressure 2",
        "calculations.ID_WEB_LIN_ND_2": "Low Pressure 2",
        "calculations.ID_WEB_Temperatur_THG_2": "Heat Source Temperature 2",
        "calculations.ID_WEB_Temperatur_TWE_2": "Evaporator Temperature 2",
        "calculations.ID_WEB_Temperatur_TFB3": "Mixed Circuit 3 Flow Temperature",
        "calculations.ID_WEB_Sollwert_TVL_MK3": "Mixed Circuit 3 Flow Temperature Setpoint",
        "calculations.ID_WEB_Temperatur_RFV2": "Room Flow Temperature 2",
        "calculations.ID_WEB_Temperatur_RFV3": "Room Flow Temperature 3",
        "calculations.ID_WEB_Temperatur_BW_oben": "Hot Water Temperature Top",
        "calculations.ID_WEB_LIN_UH_Soll": "Superheating Target Setpoint",
        "calculations.ID_WEB_LIN_UH_Soll_2": "Superheating Target Setpoint 2",
        "calculations.ID_WEB_SEC_TVL_Soll": "Secondary Flow Temperature Setpoint",
        "calculations.ID_WEB_SEC_VerdEVI": "Secondary Evaporation Temperature",
        "calculations.ID_WEB_SEC_AnsEVI": "Secondary Suction Evaporation Temperature",
        "calculations.ID_WEB_SEC_UEH_EVI": "Secondary Superheating EVI",
        "calculations.ID_WEB_SEC_UEH_EVI_S": "Secondary Superheating EVI Setpoint",
        "calculations.ID_WEB_SEC_KondTemp": "Secondary Condensation Temperature",
        "calculations.ID_WEB_SEC_FlussigEx": "Secondary Liquid Temperature",
        "calculations.ID_WEB_SEC_UK_EEV": "Secondary Expansion Valve Temperature",
        "calculations.ID_WEB_SEC_EVI_Druck": "Secondary EVI Pressure",
        "calculations.ID_WEB_SEC_U_Inv": "Secondary Inverter Voltage",
        "calculations.ID_WEB_RBE_RT_Ist": "RBE Return Temperature Actual",
        "calculations.ID_WEB_RBE_RT_Soll": "RBE Return Temperature Setpoint",
        "calculations.Vapourisation_Temperature": "Vaporization Temperature",
        "calculations.Liquefaction_Temperature": "Liquefaction Temperature",
        "calculations.DESIRED_ROOM_TEMPERATURE": "Desired Room Temperature",

        # Status and control signals
        "calculations.ID_WEB_ASDin": "ASD Input",
        "calculations.ID_WEB_BWTin": "BWT Input",
        "calculations.ID_WEB_EVUin": "EVU Input",
        "calculations.ID_WEB_HDin": "HD Input",
        "calculations.ID_WEB_MOTin": "MOT Input",
        "calculations.ID_WEB_NDin": "ND Input",
        "calculations.ID_WEB_PEXin": "PEX Input",
        "calculations.ID_WEB_SWTin": "SWT Input",
        "calculations.ID_WEB_AVout": "AV Output",
        "calculations.ID_WEB_BUPout": "BUP Output",
        "calculations.ID_WEB_HUPout": "HUP Output",
        "calculations.ID_WEB_MA1out": "MA1 Output",
        "calculations.ID_WEB_MZ1out": "MZ1 Output",
        "calculations.ID_WEB_VENout": "VEN Output",
        "calculations.ID_WEB_VBOout": "VBO Output",
        "calculations.ID_WEB_VD1out": "VD1 Output",
        "calculations.ID_WEB_VD2out": "VD2 Output",
        "calculations.ID_WEB_ZIPout": "ZIP Output",
        "calculations.ID_WEB_ZUPout": "ZUP Output",
        "calculations.ID_WEB_ZW1out": "ZW1 Output",
        "calculations.ID_WEB_ZW2SSTout": "ZW2 SST Output",
        "calculations.ID_WEB_ZW3SSTout": "ZW3 SST Output",
        "calculations.ID_WEB_FP2out": "FP2 Output",
        "calculations.ID_WEB_SLPout": "SLP Output",
        "calculations.ID_WEB_SUPout": "SUP Output",
        "calculations.ID_WEB_MZ2out": "MZ2 Output",
        "calculations.ID_WEB_MA2out": "MA2 Output",
        "calculations.ID_WEB_MA3out": "MA3 Output",
        "calculations.ID_WEB_MZ3out": "MZ3 Output",
        "calculations.ID_WEB_FP3out": "FP3 Output",
        "calculations.ID_WEB_LIN_VDH_out": "VDH Output",
        "calculations.ID_WEB_LIN_VDH_out_2": "VDH Output 2",
        "calculations.ID_WEB_HDin_2": "HD Input 2",
        "calculations.ID_WEB_AVout_2": "AV Output 2",
        "calculations.ID_WEB_VBOout_2": "VBO Output 2",
        "calculations.ID_WEB_VD1out_2": "VD1 Output 2",
        "calculations.ID_WEB_HZIO_STB": "HZIO STB",
        "calculations.ID_WEB_HZIO_EVU2": "HZIO EVU2",
        "calculations.ID_WEB_SAXin": "SAX Input",
        "calculations.ID_WEB_SPLin": "SPL Input",
        "calculations.ID_WEB_Compact_exists": "Compact Exists",
        "calculations.ID_WEB_LIN_exists": "LIN Exists",
        "calculations.ID_WEB_FreigabKuehl": "Cooling Enable",

        # Time counters and timers
        "calculations.ID_WEB_Zaehler_BetrZeitVD1": "Compressor 1 Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitImpVD1": "Compressor 1 Impulse Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitVD2": "Compressor 2 Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitImpVD2": "Compressor 2 Impulse Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitZWE1": "ZWE 1 Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitZWE2": "ZWE 2 Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitZWE3": "ZWE 3 Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitWP": "Heat Pump Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitHz": "Heating Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitBW": "Hot Water Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitKue": "Cooling Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitSW": "Swimming Pool Operating Time",
        "calculations.ID_WEB_Zaehler_BetrZeitSolar": "Solar Operating Time",
        "calculations.ID_WEB_Time_WPein_akt": "Heat Pump On Time",
        "calculations.ID_WEB_Time_ZWE1_akt": "ZWE 1 On Time",
        "calculations.ID_WEB_Time_ZWE2_akt": "ZWE 2 On Time",
        "calculations.ID_WEB_Timer_EinschVerz": "Switch-On Delay Timer",
        "calculations.ID_WEB_Time_SSPAUS_akt": "SSP Off Time",
        "calculations.ID_WEB_Time_SSPEIN_akt": "SSP On Time",
        "calculations.ID_WEB_Time_VDStd_akt": "VD Standard Time",
        "calculations.ID_WEB_Time_HRM_akt": "HRM Time",
        "calculations.ID_WEB_Time_HRW_akt": "HRW Time",
        "calculations.ID_WEB_Time_LGS_akt": "LGS Time",
        "calculations.ID_WEB_Time_SBW_akt": "SBW Time",
        "calculations.ID_WEB_Time_AbtIn": "Defrost Time",
        "calculations.ID_WEB_Time_Heissgas": "Hot Gas Time",

        # Heat pump operation data
        "calculations.ID_WEB_Code_WP_akt": "Heat Pump Code",
        "calculations.ID_WEB_Code_WP_akt_2": "Heat Pump Code 2",
        "calculations.ID_WEB_BIV_Stufe_akt": "Bivalence Level",
        "calculations.ID_WEB_WP_BZ_akt": "Heat Pump Operation Mode",
        "calculations.ID_WEB_SEC_BZ": "Secondary Operation Mode",
        "calculations.ID_WEB_SEC_VWV": "Secondary VWV",
        "calculations.ID_WEB_SEC_VD": "Secondary VD",
        "calculations.ID_WEB_Freq_VD": "Compressor Frequency",
        "calculations.ID_WEB_Freq_VD_Soll": "Compressor Frequency Setpoint",
        "calculations.ID_WEB_Freq_VD_Min": "Compressor Frequency Min",
        "calculations.ID_WEB_Freq_VD_Max": "Compressor Frequency Max",
        "calculations.ID_WEB_HZIO_PWM": "HZIO PWM",
        "calculations.ID_WEB_HZIO_VEN": "HZIO VEN",
        "calculations.HUP_PWM": "HUP PWM",
        "calculations.Flow_Rate_254": "Flow Rate",
        "calculations.Heat_Output": "Heat Output",
        "calculations.RBE_Version": "RBE Version",
        "calculations.VBO_Temp_Spread_Soll": "VBO Temperature Spread Setpoint",
        "calculations.VBO_Temp_Spread_Ist": "VBO Temperature Spread Actual",
        "calculations.HUP_Temp_Spread_Soll": "HUP Temperature Spread Setpoint",
        "calculations.HUP_Temp_Spread_Ist": "HUP Temperature Spread Actual",

        # Error and status information
        "calculations.ID_WEB_ERROR_Time0": "Error Time 0",
        "calculations.ID_WEB_ERROR_Time1": "Error Time 1",
        "calculations.ID_WEB_ERROR_Time2": "Error Time 2",
        "calculations.ID_WEB_ERROR_Time3": "Error Time 3",
        "calculations.ID_WEB_ERROR_Time4": "Error Time 4",
        "calculations.ID_WEB_ERROR_Nr0": "Error Number 0",
        "calculations.ID_WEB_ERROR_Nr1": "Error Number 1",
        "calculations.ID_WEB_ERROR_Nr2": "Error Number 2",
        "calculations.ID_WEB_ERROR_Nr3": "Error Number 3",
        "calculations.ID_WEB_ERROR_Nr4": "Error Number 4",
        "calculations.ID_WEB_AnzahlFehlerInSpeicher": "Number of Errors in Memory",
        "calculations.ID_WEB_Switchoff_file_Nr0": "Switchoff File Number 0",
        "calculations.ID_WEB_Switchoff_file_Nr1": "Switchoff File Number 1",
        "calculations.ID_WEB_Switchoff_file_Nr2": "Switchoff File Number 2",
        "calculations.ID_WEB_Switchoff_file_Nr3": "Switchoff File Number 3",
        "calculations.ID_WEB_Switchoff_file_Nr4": "Switchoff File Number 4",
        "calculations.ID_WEB_Switchoff_file_Time0": "Switchoff File Time 0",
        "calculations.ID_WEB_Switchoff_file_Time1": "Switchoff File Time 1",
        "calculations.ID_WEB_Switchoff_file_Time2": "Switchoff File Time 2",
        "calculations.ID_WEB_Switchoff_file_Time3": "Switchoff File Time 3",
        "calculations.ID_WEB_Switchoff_file_Time4": "Switchoff File Time 4",
        "calculations.ID_WEB_Switchoff2_file_Nr0": "Switchoff File 2 Number 0",
        "calculations.ID_WEB_Switchoff2_file_Nr1": "Switchoff File 2 Number 1",
        "calculations.ID_WEB_Switchoff2_file_Nr2": "Switchoff File 2 Number 2",
        "calculations.ID_WEB_Switchoff2_file_Nr3": "Switchoff File 2 Number 3",
        "calculations.ID_WEB_Switchoff2_file_Nr4": "Switchoff File 2 Number 4",
        "calculations.ID_WEB_Switchoff2_file_Time0": "Switchoff File 2 Time 0",
        "calculations.ID_WEB_Switchoff2_file_Time1": "Switchoff File 2 Time 1",
        "calculations.ID_WEB_Switchoff2_file_Time2": "Switchoff File 2 Time 2",
        "calculations.ID_WEB_Switchoff2_file_Time3": "Switchoff File 2 Time 3",
        "calculations.ID_WEB_Switchoff2_file_Time4": "Switchoff File 2 Time 4",

        # Menu and display information
        "calculations.ID_WEB_Comfort_exists": "Comfort Exists",
        "calculations.ID_WEB_HauptMenuStatus_Zeile1": "Main Menu Status Line 1",
        "calculations.ID_WEB_HauptMenuStatus_Zeile2": "Main Menu Status Line 2",
        "calculations.ID_WEB_HauptMenuStatus_Zeile3": "Main Menu Status Line 3",
        "calculations.ID_WEB_HauptMenuStatus_Zeit": "Main Menu Status Time",
        "calculations.ID_WEB_HauptMenuAHP_Stufe": "Main Menu AHP Level",
        "calculations.ID_WEB_HauptMenuAHP_Temp": "Main Menu AHP Temperature",
        "calculations.ID_WEB_HauptMenuAHP_Zeit": "Main Menu AHP Time",

        # System status indicators
        "calculations.ID_WEB_SH_BWW": "Hot Water Status",
        "calculations.ID_WEB_SH_HZ": "Heating Status",
        "calculations.ID_WEB_SH_MK1": "Mixed Circuit 1 Status",
        "calculations.ID_WEB_SH_MK2": "Mixed Circuit 2 Status",
        "calculations.ID_WEB_SH_MK3": "Mixed Circuit 3 Status",
        "calculations.ID_WEB_SH_SW": "Swimming Pool Status",
        "calculations.ID_WEB_SH_ZIP": "ZIP Status",
        "calculations.ID_WEB_WebsrvProgrammWerteBeobarten": "Web Server Program Values",

        # Software and version information
        "calculations.ID_WEB_SoftStand_0": "Software Version 0",
        "calculations.ID_WEB_SoftStand_1": "Software Version 1",
        "calculations.ID_WEB_SoftStand_2": "Software Version 2",
        "calculations.ID_WEB_SoftStand_3": "Software Version 3",
        "calculations.ID_WEB_SoftStand_4": "Software Version 4",
        "calculations.ID_WEB_SoftStand_5": "Software Version 5",
        "calculations.ID_WEB_SoftStand_6": "Software Version 6",
        "calculations.ID_WEB_SoftStand_7": "Software Version 7",
        "calculations.ID_WEB_SoftStand_8": "Software Version 8",
        "calculations.ID_WEB_SoftStand_9": "Software Version 9",
        "calculations.ID_WEB_SEC_Software": "Secondary Software",

        # Network information
        "calculations.ID_WEB_AdresseIP_akt": "Current IP Address",
        "calculations.ID_WEB_SubNetMask_akt": "Current Subnet Mask",
        "calculations.ID_WEB_Add_Broadcast": "Broadcast Address",
        "calculations.ID_WEB_Add_StdGateway": "Standard Gateway",

        # Timestamp information
        "calculations.ID_WEB_AktuelleTimeStamp": "Current Timestamp",

        # Energy and flow measurements
        "calculations.ID_WEB_WMZ_Heizung": "Energy Meter Heating",
        "calculations.ID_WEB_WMZ_Brauchwasser": "Energy Meter Hot Water",
        "calculations.ID_WEB_WMZ_Schwimmbad": "Energy Meter Swimming Pool",
        "calculations.ID_WEB_WMZ_Seit": "Energy Meter Since",
        "calculations.ID_WEB_WMZ_Durchfluss": "Flow Rate",
        "calculations.ID_WEB_Durchfluss_WQ": "Water Flow Rate",
        "calculations.ID_WEB_SEC_Qh_Soll": "Secondary Heat Output Setpoint",
        "calculations.ID_WEB_SEC_Qh_Ist": "Secondary Heat Output Actual",

        # Analog inputs and outputs
        "calculations.ID_WEB_AnalogIn": "Analog Input",
        "calculations.ID_WEB_AnalogIn2": "Analog Input 2",
        "calculations.ID_WEB_AnalogIn3": "Analog Input 3",
        "calculations.ID_WEB_AnalogOut1": "Analog Output 1",
        "calculations.ID_WEB_AnalogOut2": "Analog Output 2",
        "calculations.ID_WEB_AnalogOut3": "Analog Output 3",
        "calculations.ID_WEB_AnalogOut4": "Analog Output 4",
        "calculations.ID_WEB_Out_VZU": "Output VZU",
        "calculations.ID_WEB_Out_VAB": "Output VAB",
        "calculations.ID_WEB_Out_VSK": "Output VSK",
        "calculations.ID_WEB_Out_FRH": "Output FRH",

        # Ventilation temperatures
        "calculations.ID_WEB_Temp_Lueftung_Zuluft": "Ventilation Supply Air Temperature",
        "calculations.ID_WEB_Temp_Lueftung_Abluft": "Ventilation Exhaust Air Temperature",

        # Slave status information
        "calculations.ID_WEB_StatusSlave_1": "Slave Status 1",
        "calculations.ID_WEB_StatusSlave_2": "Slave Status 2",
        "calculations.ID_WEB_StatusSlave_3": "Slave Status 3",
        "calculations.ID_WEB_StatusSlave_4": "Slave Status 4",
        "calculations.ID_WEB_StatusSlave_5": "Slave Status 5",

        # Parameter mappings
        "parameters.ID_Einst_Heizgrenze_Temp": "Heating Limit Temperature",
        "parameters.ID_Soll_BWS_akt": "Hot Water Setpoint Actual",
        "parameters.ID_Ba_Hz_akt": "Heating Operation Mode",
        "parameters.ID_Einst_HzHKRANH_akt": "Heating Circuit Pump Operation",
        "parameters.ID_Einst_HzHKRABS_akt": "Heating Circuit Pump Standby",
        "parameters.ID_Einst_HzMK1E_akt": "Mixed Circuit 1 Enable",
        "parameters.ID_Einst_HzMK2E_akt": "Mixed Circuit 2 Enable",
        "parameters.ID_Einst_HzMK3E_akt": "Mixed Circuit 3 Enable",
        "parameters.ID_Einst_HzFtRl_akt": "Heating Return Temperature",
        "parameters.ID_Einst_HzFtRlMx_akt": "Heating Return Temperature Max",
        "parameters.ID_Einst_HzFtRlMn_akt": "Heating Return Temperature Min",
        "parameters.ID_Einst_HzFtRLs_akt": "Heating Return Temperature Setpoint",
        "parameters.ID_Einst_HzFtRLsMx_akt": "Heating Return Temperature Setpoint Max",
        "parameters.ID_Einst_HzFtRLsMn_akt": "Heating Return Temperature Setpoint Min",
        "parameters.ID_Einst_HzFtAk_akt": "Heating Flow Temperature Correction",
        "parameters.ID_Einst_HzFtAkMx_akt": "Heating Flow Temperature Correction Max",
        "parameters.ID_Einst_HzFtAkMn_akt": "Heating Flow Temperature Correction Min",
        "parameters.ID_Einst_HzFtAkAs_akt": "Heating Flow Temperature Correction Factor",
        "parameters.ID_Einst_HzFtAkAsMx_akt": "Heating Flow Temperature Correction Factor Max",
        "parameters.ID_Einst_HzFtAkAsMn_akt": "Heating Flow Temperature Correction Factor Min",
        "parameters.ID_Einst_HzFtAkAsSt_akt": "Heating Flow Temperature Correction Factor Step",
        "parameters.ID_Einst_HzFtAkAsStMx_akt": "Heating Flow Temperature Correction Factor Step Max",
        "parameters.ID_Einst_HzFtAkAsStMn_akt": "Heating Flow Temperature Correction Factor Step Min",
        "parameters.ID_Einst_HzFtAkAsStSt_akt": "Heating Flow Temperature Correction Factor Step Step",
        "parameters.ID_Einst_HzFtAkAsStStMx_akt": "Heating Flow Temperature Correction Factor Step Step Max",
        "parameters.ID_Einst_HzFtAkAsStStMn_akt": "Heating Flow Temperature Correction Factor Step Step Min",

        # Visibility mappings
        "visibilities.ID_Visi_NieAnzeigen": "Never Show",
        "visibilities.ID_Visi_ImmerAnzeigen": "Always Show",
        "visibilities.ID_Visi_Heizung": "Heating",
        "visibilities.ID_Visi_Brauwasser": "Hot Water",
        "visibilities.ID_Visi_Schwimmbad": "Swimming Pool",
        "visibilities.ID_Visi_Kuhlung": "Cooling",
        "visibilities.ID_Visi_Lueftung": "Ventilation",
        "visibilities.ID_Visi_MK1": "Mixed Circuit 1",
        "visibilities.ID_Visi_MK2": "Mixed Circuit 2",
        "visibilities.ID_Visi_MK3": "Mixed Circuit 3",
        "visibilities.ID_Visi_ThermDesinfekt": "Thermal Disinfection",
        "visibilities.ID_Visi_Zirkulation": "Circulation",
        "visibilities.ID_Visi_KuhlTemp_SolltempMK1": "Cooling Temperature Setpoint MK1",
        "visibilities.ID_Visi_KuhlTemp_SolltempMK2": "Cooling Temperature Setpoint MK2",
        "visibilities.ID_Visi_KuhlTemp_SolltempMK3": "Cooling Temperature Setpoint MK3",
        "visibilities.ID_Visi_Temp_Festwert": "Temperature Fixed Value",
        "visibilities.ID_Visi_Temp_FestwertMK1": "Temperature Fixed Value MK1",
        "visibilities.ID_Visi_Temp_FestwertMK2": "Temperature Fixed Value MK2",
        "visibilities.ID_Visi_Temp_FestwertMK3": "Temperature Fixed Value MK3",
        "visibilities.ID_Visi_Temp_Raum": "Room Temperature",
        "visibilities.ID_Visi_Temp_RaumMK1": "Room Temperature MK1",
        "visibilities.ID_Visi_Temp_RaumMK2": "Room Temperature MK2",
        "visibilities.ID_Visi_Temp_RaumMK3": "Room Temperature MK3",
        "visibilities.ID_Visi_Temp_Aussen": "Outside Temperature",
        "visibilities.ID_Visi_Temp_AussenMK1": "Outside Temperature MK1",
        "visibilities.ID_Visi_Temp_AussenMK2": "Outside Temperature MK2",
        "visibilities.ID_Visi_Temp_AussenMK3": "Outside Temperature MK3",
        "visibilities.ID_Visi_Temp_Vorlauf": "Flow Temperature",
        "visibilities.ID_Visi_Temp_VorlaufMK1": "Flow Temperature MK1",
        "visibilities.ID_Visi_Temp_VorlaufMK2": "Flow Temperature MK2",
        "visibilities.ID_Visi_Temp_VorlaufMK3": "Flow Temperature MK3",
        "visibilities.ID_Visi_Temp_Ruecklauf": "Return Temperature",
        "visibilities.ID_Visi_Temp_RuecklaufMK1": "Return Temperature MK1",
        "visibilities.ID_Visi_Temp_RuecklaufMK2": "Return Temperature MK2",
        "visibilities.ID_Visi_Temp_RuecklaufMK3": "Return Temperature MK3",
        "visibilities.ID_Visi_Temp_Warmwasser": "Hot Water Temperature",
        "visibilities.ID_Visi_Temp_WarmwasserMK1": "Hot Water Temperature MK1",
        "visibilities.ID_Visi_Temp_WarmwasserMK2": "Hot Water Temperature MK2",
        "visibilities.ID_Visi_Temp_WarmwasserMK3": "Hot Water Temperature MK3",
        "visibilities.ID_Visi_Temp_Mischkreis1": "Mixed Circuit 1 Temperature",
        "visibilities.ID_Visi_Temp_Mischkreis2": "Mixed Circuit 2 Temperature",
        "visibilities.ID_Visi_Temp_Mischkreis3": "Mixed Circuit 3 Temperature",
        "visibilities.ID_Visi_Temp_Speicher": "Storage Temperature",
        "visibilities.ID_Visi_Temp_SpeicherMK1": "Storage Temperature MK1",
        "visibilities.ID_Visi_Temp_SpeicherMK2": "Storage Temperature MK2",
        "visibilities.ID_Visi_Temp_SpeicherMK3": "Storage Temperature MK3",
        "visibilities.ID_Visi_Temp_Heissgas": "Hot Gas Temperature",
        "visibilities.ID_Visi_Temp_HeissgasMK1": "Hot Gas Temperature MK1",
        "visibilities.ID_Visi_Temp_HeissgasMK2": "Hot Gas Temperature MK2",
        "visibilities.ID_Visi_Temp_HeissgasMK3": "Hot Gas Temperature MK3",
        "visibilities.ID_Visi_Temp_Abhilfe": "Remedy Temperature",
        "visibilities.ID_Visi_Temp_AbhilfeMK1": "Remedy Temperature MK1",
        "visibilities.ID_Visi_Temp_AbhilfeMK2": "Remedy Temperature MK2",
        "visibilities.ID_Visi_Temp_AbhilfeMK3": "Remedy Temperature MK3",
        "visibilities.ID_Visi_Temp_Verdampfung": "Evaporation Temperature",
        "visibilities.ID_Visi_Temp_VerdampfungMK1": "Evaporation Temperature MK1",
        "visibilities.ID_Visi_Temp_VerdampfungMK2": "Evaporation Temperature MK2",
        "visibilities.ID_Visi_Temp_VerdampfungMK3": "Evaporation Temperature MK3",
        "visibilities.ID_Visi_Temp_Kondensation": "Condensation Temperature",
        "visibilities.ID_Visi_Temp_KondensationMK1": "Condensation Temperature MK1",
        "visibilities.ID_Visi_Temp_KondensationMK2": "Condensation Temperature MK2",
        "visibilities.ID_Visi_Temp_KondensationMK3": "Condensation Temperature MK3",
        "visibilities.ID_Visi_Temp_Ueberhitzung": "Superheating Temperature",
        "visibilities.ID_Visi_Temp_UeberhitzungMK1": "Superheating Temperature MK1",
        "visibilities.ID_Visi_Temp_UeberhitzungMK2": "Superheating Temperature MK2",
        "visibilities.ID_Visi_Temp_UeberhitzungMK3": "Superheating Temperature MK3",
        "visibilities.ID_Visi_Temp_Niederdruck": "Low Pressure Temperature",
        "visibilities.ID_Visi_Temp_NiederdruckMK1": "Low Pressure Temperature MK1",
        "visibilities.ID_Visi_Temp_NiederdruckMK2": "Low Pressure Temperature MK2",
        "visibilities.ID_Visi_Temp_NiederdruckMK3": "Low Pressure Temperature MK3",
        "visibilities.ID_Visi_Temp_Hochdruck": "High Pressure Temperature",
        "visibilities.ID_Visi_Temp_HochdruckMK1": "High Pressure Temperature MK1",
        "visibilities.ID_Visi_Temp_HochdruckMK2": "High Pressure Temperature MK2",
        "visibilities.ID_Visi_Temp_HochdruckMK3": "High Pressure Temperature MK3",
        "visibilities.ID_Visi_Temp_Verdichter": "Compressor Temperature",
        "visibilities.ID_Visi_Temp_VerdichterMK1": "Compressor Temperature MK1",
        "visibilities.ID_Visi_Temp_VerdichterMK2": "Compressor Temperature MK2",
        "visibilities.ID_Visi_Temp_VerdichterMK3": "Compressor Temperature MK3",
        "visibilities.ID_Visi_Temp_Ventilator": "Ventilator Temperature",
        "visibilities.ID_Visi_Temp_VentilatorMK1": "Ventilator Temperature MK1",
        "visibilities.ID_Visi_Temp_VentilatorMK2": "Ventilator Temperature MK2",
        "visibilities.ID_Visi_Temp_VentilatorMK3": "Ventilator Temperature MK3",
        "visibilities.ID_Visi_Temp_Waermepumpe": "Heat Pump Temperature",
        "visibilities.ID_Visi_Temp_WaermepumpeMK1": "Heat Pump Temperature MK1",
        "visibilities.ID_Visi_Temp_WaermepumpeMK2": "Heat Pump Temperature MK2",
        "visibilities.ID_Visi_Temp_WaermepumpeMK3": "Heat Pump Temperature MK3",
        "visibilities.ID_Visi_Temp_Solar": "Solar Temperature",
        "visibilities.ID_Visi_Temp_SolarMK1": "Solar Temperature MK1",
        "visibilities.ID_Visi_Temp_SolarMK2": "Solar Temperature MK2",
        "visibilities.ID_Visi_Temp_SolarMK3": "Solar Temperature MK3",
        "visibilities.ID_Visi_Temp_Feststoffkessel": "Solid Fuel Boiler Temperature",
        "visibilities.ID_Visi_Temp_FeststoffkesselMK1": "Solid Fuel Boiler Temperature MK1",
        "visibilities.ID_Visi_Temp_FeststoffkesselMK2": "Solid Fuel Boiler Temperature MK2",
        "visibilities.ID_Visi_Temp_FeststoffkesselMK3": "Solid Fuel Boiler Temperature MK3",
        "visibilities.ID_Visi_Temp_Nahwaerme": "District Heating Temperature",
        "visibilities.ID_Visi_Temp_NahwaermeMK1": "District Heating Temperature MK1",
        "visibilities.ID_Visi_Temp_NahwaermeMK2": "District Heating Temperature MK2",
        "visibilities.ID_Visi_Temp_NahwaermeMK3": "District Heating Temperature MK3",
        "visibilities.ID_Visi_Temp_Brennwert": "Condensing Boiler Temperature",
        "visibilities.ID_Visi_Temp_BrennwertMK1": "Condensing Boiler Temperature MK1",
        "visibilities.ID_Visi_Temp_BrennwertMK2": "Condensing Boiler Temperature MK2",
        "visibilities.ID_Visi_Temp_BrennwertMK3": "Condensing Boiler Temperature MK3",
        "visibilities.ID_Visi_Temp_Brauchwasser": "Domestic Hot Water Temperature",
        "visibilities.ID_Visi_Temp_BrauchwasserMK1": "Domestic Hot Water Temperature MK1",
        "visibilities.ID_Visi_Temp_BrauchwasserMK2": "Domestic Hot Water Temperature MK2",
        "visibilities.ID_Visi_Temp_BrauchwasserMK3": "Domestic Hot Water Temperature MK3",
        "visibilities.ID_Visi_Temp_Zirkulation": "Circulation Temperature",
        "visibilities.ID_Visi_Temp_ZirkulationMK1": "Circulation Temperature MK1",
        "visibilities.ID_Visi_Temp_ZirkulationMK2": "Circulation Temperature MK2",
        "visibilities.ID_Visi_Temp_ZirkulationMK3": "Circulation Temperature MK3",
        "visibilities.ID_Visi_Temp_Rueckkuehlung": "Return Cooling Temperature",
        "visibilities.ID_Visi_Temp_RueckkuehlungMK1": "Return Cooling Temperature MK1",
        "visibilities.ID_Visi_Temp_RueckkuehlungMK2": "Return Cooling Temperature MK2",
        "visibilities.ID_Visi_Temp_RueckkuehlungMK3": "Return Cooling Temperature MK3",
        "visibilities.ID_Visi_Temp_Vorlaufkuehlung": "Flow Cooling Temperature",
        "visibilities.ID_Visi_Temp_VorlaufkuehlungMK1": "Flow Cooling Temperature MK1",
        "visibilities.ID_Visi_Temp_VorlaufkuehlungMK2": "Flow Cooling Temperature MK2",
        "visibilities.ID_Visi_Temp_VorlaufkuehlungMK3": "Flow Cooling Temperature MK3",
        "visibilities.ID_Visi_Temp_Speicherkuehlung": "Storage Cooling Temperature",
        "visibilities.ID_Visi_Temp_SpeicherkuehlungMK1": "Storage Cooling Temperature MK1",
        "visibilities.ID_Visi_Temp_SpeicherkuehlungMK2": "Storage Cooling Temperature MK2",
        "visibilities.ID_Visi_Temp_SpeicherkuehlungMK3": "Storage Cooling Temperature MK3",
        "visibilities.ID_Visi_Temp_Waermetauscher": "Heat Exchanger Temperature",
        "visibilities.ID_Visi_Temp_WaermetauscherMK1": "Heat Exchanger Temperature MK1",
        "visibilities.ID_Visi_Temp_WaermetauscherMK2": "Heat Exchanger Temperature MK2",
        "visibilities.ID_Visi_Temp_WaermetauscherMK3": "Heat Exchanger Temperature MK3",
        "visibilities.ID_Visi_Temp_Ventilator2": "Ventilator 2 Temperature",
        "visibilities.ID_Visi_Temp_Ventilator2MK1": "Ventilator 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Ventilator2MK2": "Ventilator 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Ventilator2MK3": "Ventilator 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Verdichter2": "Compressor 2 Temperature",
        "visibilities.ID_Visi_Temp_Verdichter2MK1": "Compressor 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Verdichter2MK2": "Compressor 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Verdichter2MK3": "Compressor 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Niederdruck2": "Low Pressure 2 Temperature",
        "visibilities.ID_Visi_Temp_Niederdruck2MK1": "Low Pressure 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Niederdruck2MK2": "Low Pressure 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Niederdruck2MK3": "Low Pressure 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Hochdruck2": "High Pressure 2 Temperature",
        "visibilities.ID_Visi_Temp_Hochdruck2MK1": "High Pressure 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Hochdruck2MK2": "High Pressure 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Hochdruck2MK3": "High Pressure 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Verdampfung2": "Evaporation 2 Temperature",
        "visibilities.ID_Visi_Temp_Verdampfung2MK1": "Evaporation 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Verdampfung2MK2": "Evaporation 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Verdampfung2MK3": "Evaporation 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Kondensation2": "Condensation 2 Temperature",
        "visibilities.ID_Visi_Temp_Kondensation2MK1": "Condensation 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Kondensation2MK2": "Condensation 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Kondensation2MK3": "Condensation 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Ueberhitzung2": "Superheating 2 Temperature",
        "visibilities.ID_Visi_Temp_Ueberhitzung2MK1": "Superheating 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Ueberhitzung2MK2": "Superheating 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Ueberhitzung2MK3": "Superheating 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Heissgas2": "Hot Gas 2 Temperature",
        "visibilities.ID_Visi_Temp_Heissgas2MK1": "Hot Gas 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Heissgas2MK2": "Hot Gas 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Heissgas2MK3": "Hot Gas 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Abhilfe2": "Remedy 2 Temperature",
        "visibilities.ID_Visi_Temp_Abhilfe2MK1": "Remedy 2 Temperature MK1",
        "visibilities.ID_Visi_Temp_Abhilfe2MK2": "Remedy 2 Temperature MK2",
        "visibilities.ID_Visi_Temp_Abhilfe2MK3": "Remedy 2 Temperature MK3",
        "visibilities.ID_Visi_Temp_Verdichter3": "Compressor 3 Temperature",
        "visibilities.ID_Visi_Temp_Verdichter3MK1": "Compressor 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Verdichter3MK2": "Compressor 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Verdichter3MK3": "Compressor 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Niederdruck3": "Low Pressure 3 Temperature",
        "visibilities.ID_Visi_Temp_Niederdruck3MK1": "Low Pressure 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Niederdruck3MK2": "Low Pressure 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Niederdruck3MK3": "Low Pressure 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Hochdruck3": "High Pressure 3 Temperature",
        "visibilities.ID_Visi_Temp_Hochdruck3MK1": "High Pressure 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Hochdruck3MK2": "High Pressure 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Hochdruck3MK3": "High Pressure 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Verdampfung3": "Evaporation 3 Temperature",
        "visibilities.ID_Visi_Temp_Verdampfung3MK1": "Evaporation 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Verdampfung3MK2": "Evaporation 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Verdampfung3MK3": "Evaporation 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Kondensation3": "Condensation 3 Temperature",
        "visibilities.ID_Visi_Temp_Kondensation3MK1": "Condensation 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Kondensation3MK2": "Condensation 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Kondensation3MK3": "Condensation 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Ueberhitzung3": "Superheating 3 Temperature",
        "visibilities.ID_Visi_Temp_Ueberhitzung3MK1": "Superheating 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Ueberhitzung3MK2": "Superheating 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Ueberhitzung3MK3": "Superheating 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Heissgas3": "Hot Gas 3 Temperature",
        "visibilities.ID_Visi_Temp_Heissgas3MK1": "Hot Gas 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Heissgas3MK2": "Hot Gas 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Heissgas3MK3": "Hot Gas 3 Temperature MK3",
        "visibilities.ID_Visi_Temp_Abhilfe3": "Remedy 3 Temperature",
        "visibilities.ID_Visi_Temp_Abhilfe3MK1": "Remedy 3 Temperature MK1",
        "visibilities.ID_Visi_Temp_Abhilfe3MK2": "Remedy 3 Temperature MK2",
        "visibilities.ID_Visi_Temp_Abhilfe3MK3": "Remedy 3 Temperature MK3",
    }

    def __init__(self, output_dirs: Dict[str, str]):
        self.output_dirs = output_dirs
        self.logger = logging.getLogger(__name__)
        self._ensure_dirs()
        # Read readable headers setting from environment
        self.readable_headers = os.getenv("READABLE_HEADERS", "false").lower() == "true"

    def _ensure_dirs(self) -> None:
        """Create output directories if they don't exist"""
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def cleanup_old_csvs(self, retention_days: int) -> None:
        """Delete CSV files older than retention_days"""
        self.logger.debug(f"Starting CSV cleanup with {retention_days} day retention")

        if retention_days < 1:
            self.logger.warning("CSV retention days must be >= 1, skipping cleanup")
            return

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        total_freed_bytes = 0

        for dir_type, dir_path in self.output_dirs.items():
            self.logger.debug(f"Processing {dir_type} directory: {dir_path}")

            if not os.path.exists(dir_path):
                self.logger.warning(f"Directory does not exist, skipping: {dir_path}")
                continue

            # Find all CSV files in the directory
            csv_pattern = os.path.join(dir_path, "*.csv")
            csv_files = glob.glob(csv_pattern)
            self.logger.debug(f"Found {len(csv_files)} CSV files in {dir_path}")

            for file_path in csv_files:
                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # Delete if older than cutoff date
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        total_freed_bytes += file_size
                        self.logger.info(f"Deleted old {dir_type} CSV: {os.path.basename(file_path)} "
                                       f"(modified: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}, "
                                       f"size: {file_size} bytes)")
                except Exception as e:
                    self.logger.warning(f"Failed to process {file_path} for cleanup: {str(e)}")
                    self.logger.warning(f"Error type: {type(e).__name__}")

        if deleted_count > 0:
            # Convert bytes to MB for readable logging
            freed_mb = total_freed_bytes / (1024 * 1024)
            self.logger.info(f"CSV cleanup completed: {deleted_count} files deleted, {freed_mb:.2f} MB freed")
        else:
            self.logger.info("CSV cleanup completed: No old files found")

    def generate_daily_csv(self, data: List[Dict], date: datetime) -> str:
        """Generate daily CSV file for given date"""
        filename = f"{date.strftime('%Y-%m-%d')}_daily.csv"
        filepath = os.path.join(self.output_dirs["daily"], filename)

        self._write_csv(filepath, data)
        return filepath

    def generate_weekly_csv(self, data: List[Dict], date: datetime) -> str:
        """Generate weekly CSV file for week containing given date"""
        filename = f"{date.strftime('%Y-%m-%d')}_weekly.csv"
        filepath = os.path.join(self.output_dirs["weekly"], filename)

        self._write_csv(filepath, data)
        return filepath

    def _convert_to_readable_name(self, raw_id: str) -> str:
        """Convert raw sensor ID to human-readable name if mapping exists"""
        return self.SENSOR_NAME_MAPPINGS.get(raw_id, raw_id)

    def _should_include_field(self, field_name: str) -> bool:
        """Determine if a field should be included in the CSV output.

        When readable_headers is enabled, only include fields that have mappings.
        When readable_headers is disabled, include all fields.
        """
        if not self.readable_headers:
            return True

        # When readable_headers is enabled, only include fields with mappings
        return field_name in self.SENSOR_NAME_MAPPINGS

    def _get_readable_fieldnames(self, fieldnames: List[str]) -> List[str]:
        """Convert fieldnames to readable names if readable_headers is enabled"""
        if not self.readable_headers:
            return fieldnames

        # Filter to only include fields that have mappings, then convert to readable names
        filtered_fieldnames = [field for field in fieldnames if self._should_include_field(field)]
        return [self._convert_to_readable_name(field) for field in filtered_fieldnames]

    def _write_csv(self, filepath: str, data: List[Dict]) -> None:
        """Write data to CSV file with headers"""
        self.logger.debug(f"Writing CSV file: {filepath} with {len(data)} data points")

        if not data:
            self.logger.warning(f"No data to write to {filepath}")
            return

        try:
            # Get original fieldnames
            original_fieldnames = list(data[0]["data"].keys())

            # Convert to readable fieldnames if enabled
            fieldnames = self._get_readable_fieldnames(original_fieldnames)

            # Create a mapping from original to readable fieldnames (only for included fields)
            if self.readable_headers:
                fieldname_mapping = {
                    original: readable
                    for original, readable in zip(original_fieldnames, fieldnames)
                    if original in self.SENSOR_NAME_MAPPINGS  # Only map fields with mappings
                }
            else:
                fieldname_mapping = {
                    original: readable
                    for original, readable in zip(original_fieldnames, fieldnames)
                }

            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                row_count = 0
                for point in data:
                    # Convert data keys to readable names if needed
                    if self.readable_headers:
                        readable_data = {
                            fieldname_mapping[key]: value
                            for key, value in point["data"].items()
                            if key in fieldname_mapping  # Only include mapped fields
                        }
                        writer.writerow(readable_data)
                    else:
                        writer.writerow(point["data"])
                    row_count += 1
            self.logger.info(f"Successfully wrote CSV file: {filepath} with {row_count} rows")
        except Exception as e:
            self.logger.error(f"Failed to write CSV file {filepath}: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            raise
