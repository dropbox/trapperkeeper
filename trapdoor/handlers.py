from datetime import datetime
from sqlalchemy import func
from sqlalchemy import desc

from trapdoor.utils import TrapdoorHandler
from trapperkeeper.models import Notification


class Index(TrapdoorHandler):
    def get(self):

        now = datetime.now()

        traps = (self.db
            .query(
                Notification.host,
                Notification.oid,
                Notification.sent,
                func.max(Notification.expires).label("expires"))
            .filter(Notification.expires >= now)
            .group_by(Notification.host, Notification.oid)
            .order_by(desc(Notification.sent))
            .all()
        )

        traps += (self.db
            .query(
                Notification.host,
                Notification.oid,
                Notification.sent,
                Notification.expires)
            .filter(Notification.expires < now)
            .order_by(desc(Notification.sent))
            .limit(100)
            .all()
        )
        self.render("index.html", traps=traps, now=now)


class NotFound(TrapdoorHandler):
    def get(self):
        return self.notfound()

