import tornado.web

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
    return date_obj.strftime("%Y-%m-%d %I:%M %p")


FILTERS = {
    "print_date": print_date,
}
