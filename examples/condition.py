import logging

from dff.core import Context, Actor

logger = logging.getLogger(__name__)


def is_sf(sf_name="Open.Give.Opinion"):
    def is_sf_handler(ctx: Context, actor: Actor, *args, **kwargs):
        return sf_name in ctx.misc.get("speech_functions", [[]])[-1]

    return is_sf_handler
