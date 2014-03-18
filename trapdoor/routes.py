
from trapdoor import handlers

HANDLERS = [
    (r"/", handlers.Index),
    (r"/.*", handlers.NotFound),
]
