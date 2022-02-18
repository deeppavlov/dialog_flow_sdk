import logging

from dff.core import Context, Actor

logger = logging.getLogger(__name__)


def is_sf(sf_name="Open.Give.Opinion"):
    def is_sf_handler(ctx: Context, actor: Actor, *args, **kwargs):
        return sf_name in ctx.misc.get("speech_functions", [[""]])[-1][-1]

    return is_sf_handler


def is_midas(midas_name="pos_answer", treshhold=0.5):
    def is_midas_handler(ctx: Context, actor: Actor, *args, **kwargs):
        return midas_name in [key for key, val in ctx.misc.get("midas", [{}])[-1].items() if val > treshhold]

    return is_midas_handler


def is_intent(intent_name="topic_switching"):
    def is_intent_handler(ctx: Context, actor: Actor, *args, **kwargs):
        return intent_name in ctx.misc.get("intents", [[]])[-1]

    return is_intent_handler


def is_ext_sf(ext_sf_name="React.Respond.Support.Reply.Agree"):
    def is_ext_sf_handler(ctx: Context, actor: Actor, *args, **kwargs):
        return ext_sf_name in ctx.misc.get("ext_sf", [[]])[-1]

    return is_ext_sf_handler


speech_functions = is_sf
