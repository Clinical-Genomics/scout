"""
commands/utils.py

Helper functions for cli functions

"""

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

