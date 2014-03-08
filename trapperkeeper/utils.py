import re

_TIME_STRING_RE = re.compile(
    r'(?:(?P<days>\d+)d)?'
    r'(?:(?P<hours>\d+)h)?'
    r'(?:(?P<minutes>\d+)m)?'
    r'(?:(?P<seconds>\d+)s)?'
)

def parse_time_string(time_string):
    times = _TIME_STRING_RE.match(time_string).groupdict()
    for key, value in times.iteritems():
        if value is None:
            times[key] = 0
        else:
            times[key] = int(value)

    return times

