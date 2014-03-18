
from trapdoor.utils import TrapdoorHandler


class Index(TrapdoorHandler):
    def get(self):
        self.render("templates/index.html")


class NotFound(TrapdoorHandler):
    def get(self):
        return self.notfound()

