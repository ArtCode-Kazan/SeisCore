import datetime


d1=datetime.datetime(year=2018, month=9, day=14, hour=10,minute=5,
                     second=15,microsecond=99999)

d2 = d1.date() - datetime.timedelta(seconds=5)
print(d1.date(), d2)
d2=datetime.datetime(year=d1.year, month=d1.month,
                     day=d1.day)+datetime.timedelta(
    days=1)-datetime.timedelta(microseconds=1)

dt=(d2-d1).total_seconds()

d3 = d1+datetime.timedelta(seconds=dt)

print(d1)
print(d2)
print(dt)
print(d3)