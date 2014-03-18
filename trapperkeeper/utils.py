from jinja2 import Environment, PackageLoader
import logging
from oid_translate import ObjectId
import re
import struct
import socket

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


_TIME_STRING_RE = re.compile(
    r'(?:(?P<days>\d+)d)?'
    r'(?:(?P<hours>\d+)h)?'
    r'(?:(?P<minutes>\d+)m)?'
    r'(?:(?P<seconds>\d+)s)?'
)

DATEANDTIME_SLICES = (
    (slice(1, None, -1), "h"), # year
    (2, "b"),  # month
    (3, "b"),  # day
    (4, "b"),  # hour
    (5, "b"),  # minutes
    (6, "b"),  # seconds
    (7, "b"),  # deci seconds
    (8, "c"),  # direction from UTC
    (9, "b"),  # hours from UTC
    (10, "b"), # minutes from UTC
)


def parse_time_string(time_string):
    times = _TIME_STRING_RE.match(time_string).groupdict()
    for key, value in times.iteritems():
        if value is None:
            times[key] = 0
        else:
            times[key] = int(value)

    return times


def _to_mibname_filter(value):
    return ObjectId(value).name


def _varbind_value_filter(value):
    output = value.value
    objid = ObjectId(value.oid)

    if value.value_type == "ipaddress":
        try:
            name = socket.gethostbyaddr(value.value)[0]
            output = "%s (%s)" % (name, output)
        except socket.error:
            pass
    elif value.value_type == "oid":
        output = _to_mibname_filter(value.value)
    elif value.value_type == "octet":
        if objid.textual == "DateAndTime":
            output = decode_date(value.value)

    if objid.enums and value.value.isdigit():
        val = int(value.value)
        output = objid.enums.get(val, val)

    if objid.units:
        output = "%s %s" % (output, objid.units)

    return output


def decode_date(hex_string):
    format_values = []
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:].decode("hex")
    for _slice in DATEANDTIME_SLICES:
        format_values.append(
            struct.unpack(_slice[1], hex_string[_slice[0]])[0]
        )
    return "%d-%d-%d,%d:%d:%d.%d,%s%d:%d" % tuple(format_values)


def hostname_or_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.error:
        return ip


def get_template_env():
    filters = {
        "to_mibname": _to_mibname_filter,
        "varbind_value": _varbind_value_filter,
        "hostname_or_ip": hostname_or_ip,
    }
    env = Environment(loader=PackageLoader('trapperkeeper', 'templates'))
    env.filters.update(filters)
    return env


def send_trap_email(recipients, sender, subject, template_env, context):
    text_template = template_env.get_template("default_email_text.tmpl").render(**context)
    html_template = template_env.get_template("default_email_html.tmpl").render(**context)

    text = MIMEText(text_template, 'plain')
    html = MIMEText(html_template, 'html')

    if isinstance(recipients, basestring):
        recipients = recipients.split(",")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg.attach(text)
    msg.attach(html)

    smtp = smtplib.SMTP("localhost")  # TODO(gary): Allow config for this.
    smtp.sendmail(sender, recipients, msg.as_string())
    smtp.quit()


def get_loglevel(args):
    verbose = args.verbose * 10
    quiet = args.quiet * 10
    return logging.getLogger().level - verbose + quiet

