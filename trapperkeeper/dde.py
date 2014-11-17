from copy import deepcopy
from oid_translate import ObjectId


class DdeNotification(object):
    def __init__(self, notification, handler):
        self._notification = notification
        self.handler = deepcopy(handler)

    @property
    def host(self):
        return self._notification.host

    @property
    def sent(self):
        return self._notification.sent

    @property
    def trap_type(self):
        return self._notification.trap_type

    @property
    def request_id(self):
        return self._notification.request_id

    @property
    def version(self):
        return self._notification.version

    @property
    def notification(self):
        return ObjectId(self._notification.oid)

    @property
    def varbinds(self):
        return [
            (ObjectId(varbind.oid), varbind.value_type, varbind.value)
            for varbind in self._notification.varbinds
        ]

    @property
    def severity(self):
        return self.handler["severity"]

    @severity.setter
    def severity(self, severity):
        self.handler["severity"] = severity

    @property
    def expiration(self):
        return self.handler["expiration"]

    @expiration.setter
    def expiration(self, expiration):
        self.handler["expiration"] = expiration

    @property
    def blackhole(self):
        return self.handler["blackhole"]

    @blackhole.setter
    def blackhole(self, blackhole):
        self.handler["blackhole"] = blackhole

    @property
    def mail_recipients(self):
        return self.handler.get("mail", {}).get("recipients")

    @mail_recipients.setter
    def mail_recipients(self, recipients):
        if "mail" not in self.handler:
            self.handler["mail"] = {}
        self.handler["mail"]["recipients"] = recipients

    @property
    def mail_subject(self):
        return self.handler.get("mail", {}).get("subject")

    @mail_subject.setter
    def mail_subject(self, subject):
        if "mail" not in self.handler:
            self.handler["mail"] = {}
        self.handler["mail"]["subject"] = subject


    # Deprecated handlers

    def set_severity(self, severity):
        self.handler["severity"] = severity

    def set_expiration(self, expiration):
        self.handler["expiration"] = expiration

    def set_blackhole(self, blackhole):
        self.handler["blackhole"] = blackhole

    def set_mail_recipients(self, recipients):
        if "mail" not in self.handler:
            self.handler["mail"] = {}
        self.handler["mail"]["recipients"] = recipients

    def set_mail_subject(self, subject):
        if "mail" not in self.handler:
            self.handler["mail"] = {}
        self.handler["mail"]["subject"] = subject


