import numpy as np
from SeisCore.HydroFracCore.CalcFunctions.PointsSelection import calc_time_delay

a=[1,2,3,4,5,6]

b=[[13467921.0152,6575134.579],
    [13467640.0578,6575604.8697],
    [13467850.1402,6575513.9577],
    [13467939.5255,6575301.5304],
    [13467852.2489,6575090.5994],
    [13467640.6216,6575003.2756]]

res=calc_time_delay(points_numbers=a,points_coords=b,radius=60,
                    frequency=1000,velocity=4000,max_depth=230)

print(res)

