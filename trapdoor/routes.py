
from trapdoor import handlers

HANDLERS = [
    (r"/", handlers.Index),
    (r"/traps/?", handlers.Traps),
    (r"/resolve/?", handlers.Resolve),
    (r"/resolve_all/?", handlers.ResolveAll),
    (r"/.*", handlers.NotFound),
]
