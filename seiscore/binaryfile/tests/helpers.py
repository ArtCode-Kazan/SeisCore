

def create_latitude_str(val: float) -> str:
    degrees = int(val)
    degrees_str = str(degrees).zfill(2)

    minutes = abs(val - degrees) * 60
    minutes_str = str(minutes)

    numerical_part = f'{degrees_str}{minutes_str}'[:7]
    return numerical_part.ljust(7, '0') + 'N'


def create_longitude_str(val: float) -> str:
    degrees = int(val)
    degrees_str = str(degrees).zfill(3)
    minutes = abs(val - degrees) * 60
    minutes_str = str(minutes)
    numerical_part = f'{degrees_str}{minutes_str}'[:8]
    return numerical_part.ljust(8, '0') + 'E'
