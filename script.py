import sys
import numpy as np
import pandas as pd

def compute_runoff(rain):
    if(rain < 0):
        return None
    if(rain < 25):
        return 0.2*rain
    if(rain < 50):
        return 0.3*rain
    if(rain < 75):
        return 0.4*rain
    if(rain < 100):
        return 0.5*rain
    return 0.7*rain

def compute_data(prev_sm, rain, soil_quality):
    gamma = 0.2 if(soil_quality == "deep") else 0.4
    C = 100 if(soil_quality == "deep") else 42
    runoff = compute_runoff(rain)

    infiltration = rain + prev_sm - runoff
    crop_uptake = min(infiltration, 4)
    effective_infil = infiltration - crop_uptake
    excess = max(effective_infil - C, 0)
    sm_plus_gw = effective_infil - excess

    sm = sm_plus_gw/(1+gamma)
    gw = sm_plus_gw - sm

    return rain, runoff + excess, crop_uptake, sm, gw

if __name__=="__main__":
    n = len(sys.argv)
    if(n != 2):
        sys.exit("Wrong arguments passed")
    
    soil_quality = sys.argv[1]
    if(soil_quality != "deep" and soil_quality != "shallow"):
        sys.exit("Please enter soil quality as 'deep' or 'shallow'")
    
    df = pd.read_csv("daily_rainfall_jalgaon_chalisgaon_talegaon_2022.csv")
    file = open("output/{type}_sm.csv".format(type=soil_quality), "w")
    file.write("date,rain_mm,total_runoff_mm,crop_water_uptake_mm,soil_moisture_mm,percolation_to_groundwater_mm\n")

    prev_sm = 0
    for i in range(len(df["rain_mm"])):
        data = compute_data(prev_sm, df["rain_mm"][i], soil_quality)
        
        file.write(df["date"][i])
        for j in range(len(data)):
            file.write("," + str(data[j]))
        file.write("\n")
        
        prev_sm = data[3]
    file.close()
    
    output_df = pd.read_csv("output/{type}_sm.csv".format(type=soil_quality))
    data_valid = True

    prev_sm = 0
    for i in range(np.shape(output_df)[0]):
        temp = output_df["soil_moisture_mm"][i] - prev_sm + output_df["total_runoff_mm"][i] + output_df["crop_water_uptake_mm"][i] + output_df["percolation_to_groundwater_mm"][i]
        prev_sm = output_df["soil_moisture_mm"][i]
        if(temp - output_df["rain_mm"][i] > 0.000001):
            data_valid = False
    
    print("Validity of output data : " + str(data_valid))