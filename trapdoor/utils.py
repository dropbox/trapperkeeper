import pytz
import tornado.web
import urllib

from trapdoor.settings import settings


class TrapdoorHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = self.application.my_settings.get("db_session")()
        self.debug = self.application.my_settings.get("debug", False)
        self.debug_user = self.application.my_settings.get("debug_user")

    def on_finish(self):
        self.db.close()

    def render_template(self, template_name, **kwargs):
        template = self.application.my_settings["template_env"].get_template(template_name)
        content = template.render(kwargs)
        return content

    def render(self, template_name, **kwargs):
        kwargs.update(self.get_template_namespace())
        self.write(self.render_template(template_name, **kwargs))

    def notfound(self):
        self.set_status(404)
        self.render("errors/notfound.html")


def print_date(date_obj):
    if date_obj is None:
        return ""

    date_obj = date_obj.astimezone(settings["timezone"])
    return date_obj.strftime(settings["date_format"])


jinja2_filters = {
    "print_date": print_date,
}


def update_qs(qs, **kwargs):
    qs = qs.copy()
    qs.update(kwargs)
    return "?" + urllib.urlencode(qs, True)

jinja2_globals = {
    "update_qs": update_qs,
}
