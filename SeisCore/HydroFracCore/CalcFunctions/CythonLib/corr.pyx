def corr(int[:] a, int[:] b):
    cdef size_t i
    cdef int total = 0
    arr_size = a.shape[0]

    cdef int sum_a =0
    cdef int sum_b =0
    for i in range(arr_size):
        sum_a+=a[i]
        sum_b+=b[i]

    cdef float a_mean = sum_a*1.0/arr_size
    cdef float b_mean = sum_b*1.0/arr_size

    cdef float  sum_q = 0
    cdef float  sum_w = 0
    cdef float  sum_e = 0

    for i in range(arr_size):
        sum_q+=(a[i]-a_mean)*(b[i]-b_mean)
        sum_w+=pow((a[i]-a_mean),2)
        sum_e+=pow((b[i]-b_mean),2)

    cdef float result =0

    result = abs(sum_q/(pow(sum_w*sum_e,0.5)))

    return result




