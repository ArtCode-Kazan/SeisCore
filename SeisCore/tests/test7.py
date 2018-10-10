

a = [10, 100, 113, 30, 70, 90, 310, 350, 1000, 30, 1000, 315, 340]
moment_interval = 50

max_corr_pos = [a[0]]
for i in range(1, len(a)):
    for c in max_corr_pos:
        cc = c
        ii = i
        aa = a[i]
        if abs(c - a[i]) < moment_interval:
            break
    else:
        max_corr_pos.append(a[i])

print(max_corr_pos)


# sort_res = [[10,11,0.9], [100,101,0.85], [113, 114, 0.8]]
# max_corr_pos = [sort_res[0][0]]
# for i in range(1, len(sort_res)):
#     for c in max_corr_pos:
#         if abs(c - sort_res[i][0]) < moment_interval:
#             break
#         else:
#             max_corr_pos.append(sort_res[i][0])
#
# print (max_corr_pos)