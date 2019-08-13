from SeisCore.BinaryFile.BinaryFile import BinaryFile


bin_data=BinaryFile()
bin_data.path=r'/media/michael/Data/Projects/GRP/DemkinskoeDeposit' \
              r'/Demkinskoye_data/4772-4773/Mail/DM04_063_122_2019-07-30_07-14-11/DM04_063_122_2019-07-30_07-14-11.xx'
# bin_data.signal_frequency=1000
bin_data.record_type='ZXY'
# bin_data.read_date_time_start=datetime.datetime(year=2019, month=7, day=28,
#                                                 hour=13, minute=0, second=0)
# bin_data.read_date_time_stop=bin_data.read_date_time_start+datetime\
#     .timedelta(hours=1)
# signal=bin_data.signals
print(bin_data.datetime_start, bin_data.datetime_stop)
print(bin_data.signals.shape)
