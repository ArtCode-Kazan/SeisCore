from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import nodes, calc_time


x1 = 0
y1 = 0
x2 = -62.3100000005215
y2 = 45.0949999997392

extent = 400
velocity = 4706.85579196217
frequency = 1000

nodes_coords=nodes(extent=extent)
for el in nodes_coords:
    print(el)

min_delta_moments = 99999999
max_delta_moments = -9999999
for x_node, y_node in nodes_coords:
    time_a = calc_time(x1=x1,
                       y1=y1,
                       z1=0,
                       x2=x_node,
                       y2=y_node,
                       z2=2000,
                       velocity=velocity)

    time_b = calc_time(x1=x2,
                       y1=y2,
                       z1=0,
                       x2=x_node,
                       y2=y_node,
                       z2=2000,
                       velocity=velocity)
    delta_moments = int(round(frequency * (time_b - time_a)))
    if delta_moments < min_delta_moments:
        min_delta_moments = delta_moments
    if delta_moments > max_delta_moments:
        max_delta_moments = delta_moments

print(min_delta_moments, max_delta_moments)
