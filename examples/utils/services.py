import logging

from dff.core import Context
import requests
from nltk.tokenize import sent_tokenize


SF_URL = "http://0.0.0.0:8108/model"
MIDAS_URL = "http://0.0.0.0:8090/model"

logger = logging.getLogger(__name__)

def get_sf(ctx: Context):
    last_response = ctx.last_response
    last_request = ctx.last_request
    prev_speech_function = ctx.misc.get("speech_functions", [[None]])[-1][-1]
    requested_data = {
        "phrase": sent_tokenize(last_request),
        "prev_phrase": last_response,
        "prev_speech_function": prev_speech_function,
    }
    speech_functions = requests.post(SF_URL, json=requested_data).json()
    logger.info(f"speech_functions={speech_functions}")
    ctx.misc["speech_functions"] = ctx.misc.get("speech_functions", []) + speech_functions
    return ctx


def get_midas(ctx: Context):
    last_response = ctx.last_response if ctx.last_response else "hi"
    requested_data = {
        "dialogs": [{"human_utterances": [{"text": ctx.last_request}], "bot_utterances": [{"text": last_response}]}]
    }
    midas = requests.post(MIDAS_URL, json=requested_data).json()[0]
    logger.info(f"midas={midas}")
    ctx.misc["midas"] = ctx.misc.get("midas", []) + midas
    return ctx
