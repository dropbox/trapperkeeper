import datetime
from jinja2 import Environment, PackageLoader
import logging
from oid_translate import ObjectId
import pytz
import re
import struct
import socket
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


_TIME_STRING_RE = re.compile(
    r"(?:(?P<days>\d+)d)?"
    r"(?:(?P<hours>\d+)h)?"
    r"(?:(?P<minutes>\d+)m)?"
    r"(?:(?P<seconds>\d+)s)?"
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


def to_mibname(oid):
    return ObjectId(oid).name


def varbind_pretty_value(varbind):
    output = varbind.value
    objid = ObjectId(varbind.oid)

    if varbind.value_type == "ipaddress":
        try:
            name = socket.gethostbyaddr(varbind.value)[0]
            output = "%s (%s)" % (name, output)
        except socket.error:
            pass
    elif varbind.value_type == "oid":
        output = to_mibname(varbind.value)
    elif varbind.value_type == "octet":
        if objid.textual == "DateAndTime":
            output = decode_date(varbind.value)

    if objid.enums and varbind.value.isdigit():
        val = int(varbind.value)
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


def get_template_env(package="trapperkeeper", **kwargs):
    filters = {
        "to_mibname": to_mibname,
        "varbind_value": varbind_pretty_value,
    }
    filters.update(kwargs)
    env = Environment(loader=PackageLoader(package, "templates"))
    env.filters.update(filters)
    return env


def send_trap_email(recipients, sender, subject, template_env, context):
    text_template = template_env.get_template("default_email_text.tmpl").render(**context)
    html_template = template_env.get_template("default_email_html.tmpl").render(**context)

    text = MIMEText(text_template, "plain")
    html = MIMEText(html_template, "html")

    if isinstance(recipients, basestring):
        recipients = recipients.split(",")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(text)
    msg.attach(html)

    smtp = smtplib.SMTP("localhost")  # TODO(gary): Allow config for this.
    smtp.sendmail(sender, recipients, msg.as_string())
    smtp.quit()


def get_loglevel(args):
    verbose = args.verbose * 10
    quiet = args.quiet * 10
    return logging.getLogger().level - verbose + quiet


class CachingResolver(object):

    def __init__(self, timeout):
        self.timeout = timeout
        self._cache = {}

    def _hostname_or_ip(self, address):
        try:
            return socket.gethostbyaddr(address)[0]
        except socket.error:
            return address

    def hostname_or_ip(self, address):
        result = self._cache.get(address, None)
        now = time.time()
        if result is None or result[0] <= now:
            logging.debug("Cache miss for %s in hostname_or_ip", address)
            result = (
                now + self.timeout,             # Expiration
                self._hostname_or_ip(address),  # Data
            )
            self._cache[address] = result

        return result[1]


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
