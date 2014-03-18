import tornado.web


def print_date(date_obj):
    return date_obj.strftime("%Y-%m-%d %I:%M %p")


class TrapdoorHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = self.application.my_settings.get("db_session")()
        self.debug = self.application.my_settings.get("debug", False)
        self.debug_user = self.application.my_settings.get("debug_user")

    def on_finish(self):
        self.db.close()

    def get_template_namespace(self):
        namespace = super(TrapdoorHandler, self).get_template_namespace()
        namespace.update({
            "print_date": print_date,
        })
        return namespace

    def get_current_user(self):
        username = self.debug_user
        if not username:
            username = self.request.headers.get("X-Pp-User")

        if not username:
            return

        username = username.split("@")[0]

        user = self.db.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            self.db.add(user)
            self.db.commit()

        return user

    def notfound(self):
        self.set_status(404)
        self.render("templates/errors/notfound.html")
