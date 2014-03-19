from datetime import datetime
from sqlalchemy import desc, func, or_

from trapdoor.utils import TrapdoorHandler
from trapperkeeper.models import Notification


class Index(TrapdoorHandler):
    def get(self):

        now = datetime.now()

        traps = (self.db
            .query(
                Notification.id,
                Notification.host,
                Notification.oid,
                Notification.sent,
                func.max(Notification.expires).label("expires"))
            .filter(or_(
                Notification.expires >= now,
                Notification.expires == None
             ))
            .group_by(Notification.host, Notification.oid)
            .order_by(desc(Notification.sent))
            .all()
        )

        traps += (self.db
            .query(
                Notification.id,
                Notification.host,
                Notification.oid,
                Notification.sent,
                Notification.expires)
            .filter(Notification.expires < now)
            .order_by(desc(Notification.sent))
            .limit(100)
            .all()
        )
        return self.render("index.html", traps=traps, now=now)

class Resolve(TrapdoorHandler):
    def post(self):
        hostname = self.get_arguments("host")
        oid = self.get_arguments("oid")

        if len(hostname) != 1 or len(oid) != 1:
            return badrequest()

        hostname = hostname[0]
        oid = oid[0]
        now = datetime.now()

        traps = (self.db.query(Notification)
            .filter(
                Notification.host == hostname,
                Notification.oid == oid,
                or_(
                    Notification.expires >= now,
                    Notification.expires == None
                )
            )
            .all()
        )

        for trap in traps:
            trap.expires = now
        self.db.commit()

        return self.redirect("/")

class ResolveAll(TrapdoorHandler):
    def post(self):

        now = datetime.now()
        traps = (self.db.query(Notification)
            .filter(
                or_(
                    Notification.expires >= now,
                    Notification.expires == None
                )
            )
            .all()
        )

        for trap in traps:
            trap.expires = now
        self.db.commit()

        return self.redirect("/")

class NotFound(TrapdoorHandler):
    def get(self):
        return self.notfound()

