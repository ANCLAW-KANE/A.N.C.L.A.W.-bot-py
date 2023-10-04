from . import err,genertion_func,type_handlers,commands,kb_handler

rout = [
    err.router,
    kb_handler.router,
    commands.router,
    genertion_func.router,
    type_handlers.router
]

__all__ = ["rout"]