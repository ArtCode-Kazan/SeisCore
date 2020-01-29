import numpy as np
import segyio


class Reader:
    def __init__(self, path, time_delay, frequency, component='Z',
                 record_type='XYZ'):
        self.__path=path
        self.__time_delay=time_delay
        self.__frequency=frequency
        self.__component=component
        self.__record_type=record_type
        self.__depth_list=None

    @property
    def discrete_amount(self):
        return int(self.__frequency*self.__time_delay)

    @property
    def time_line(self):
        return np.linspace(0, self.__time_delay, self.discrete_amount)

    @property
    def depth_list(self):
        if self.__depth_list is None:
            result=list()
            with segyio.open(self.__path, ignore_geometry=True) as handle:
                trace_count = handle.tracecount
                for i in range(trace_count):
                    trace_header = handle.header[i]
                    source_x = trace_header[segyio.TraceField.SourceX]
                    if source_x not in result:
                        result.append(source_x)
            self.__depth_list=result
        return self.__depth_list

    @property
    def sensor_count(self):
        return len(self.depth_list)

    def read_data(self):
        discreet_count = self.discrete_amount
        out_data = np.zeros(shape=(discreet_count, 1))
        out_data[:, 0] = self.time_line
        depths = dict()
        with segyio.open(self.__path, ignore_geometry=True) as handle:
            trace_count = handle.tracecount
            for i in range(trace_count):
                trace_header = handle.header[i]
                source_x = trace_header[segyio.TraceField.SourceX]
                if source_x not in depths:
                    depths[source_x] = 1
                else:
                    depths[source_x] += 1

                if depths[source_x] == self.__record_type.index(self.__component) + 1:
                    out_data = np.column_stack((out_data, handle.trace[i]))
        return out_data
