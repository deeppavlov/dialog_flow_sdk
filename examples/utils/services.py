import logging
import os

from dff.core import Context
import requests
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

SF_URL = os.getenv("SF_URL", "http://0.0.0.0:8108/model")
SFP_URL = os.getenv("SFP_URL", "http://0.0.0.0:8107/model")
MIDAS_URL = os.getenv("MIDAS_URL", "http://0.0.0.0:8090/model")
ENTITY_DETECTION_URL = os.getenv("ENTITY_DETECTION_URL", "http://0.0.0.0:8103/respond")
ENTITY_LINKING_URL = os.getenv("ENTITY_LINKING_URL", "http://0.0.0.0:8075/model")
WIKI_PARSER_URL = os.getenv("WIKI_PARSER_URL", "http://0.0.0.0:8077/model")


def get_sf(ctx: Context):
    try:
        last_response = ctx.last_response
        last_request = ctx.last_request
        prev_speech_function = ctx.misc.get("speech_functions", [[None]])[-1][-1]
        requested_data = {
            "phrase": sent_tokenize(last_request),
            "prev_phrase": last_response,
            "prev_speech_function": prev_speech_function,
        }
        speech_functions = requests.post(SF_URL, json=requested_data).json()
        logger.info(f"current speech function {speech_functions}")
        ctx.misc["speech_functions"] = ctx.misc.get("speech_functions", []) + speech_functions
    except requests.exceptions.ConnectionError as exc:
        logger.warning(exc)
    return ctx


def get_sfp(ctx: Context):
    try:
        last_sf = ctx.misc.get("speech_functions", [[None]])[-1][-1]
        requested_data = [last_sf]
        sf_predictions = requests.post(SFP_URL, json=requested_data).json()
        ctx.misc["sf_predictions"] = ctx.misc.get("sf_predictions", []) + [sf_predictions[-1][0]["prediction"]]
    except requests.exceptions.ConnectionError as exc:
        logger.warning(exc)
    return ctx


def get_midas(ctx: Context):
    try:
        last_response = ctx.last_response if ctx.last_response else "hi"
        requested_data = {
            "dialogs": [{"human_utterances": [{"text": ctx.last_request}], "bot_utterances": [{"text": last_response}]}]
        }
        midas = requests.post(MIDAS_URL, json=requested_data).json()[0]
        logger.info(f"midas {midas}")
        ctx.misc["midas"] = ctx.misc.get("midas", []) + midas
    except requests.exceptions.ConnectionError as exc:
        logger.warning(exc)
    return ctx


def get_entities(ctx: Context):
    try:
        last_request = ctx.last_request if ctx.last_request else ""
        bot_utterances = list(ctx.responses.values())
        requested_data = {"last_utterances": [[last_request]]}
        if len(bot_utterances) > 0:
            requested_data["prev_utterances"] = [[bot_utterances[-1]]]
        entities = requests.post(ENTITY_DETECTION_URL, json=requested_data).json()
        logger.info(f"entity detection {entities}")
        ctx.misc["entity_detection"] = ctx.misc.get("entity_detection", []) + entities
    except requests.exceptions.ConnectionError as exc:
        logger.warning(exc)
    return ctx


def get_entity_ids(ctx: Context):
    try:
        last_request = ctx.last_request if ctx.last_request else ""
        entities = ctx.misc.get("entity_detection", [{}])[-1].get("entities", [])
        requested_data = {"entity_substr": [entities], "template": [""], "context": [[last_request]]}
        el_output = requests.post(ENTITY_LINKING_URL, json=requested_data).json()
        logger.info(f"entity_linking {el_output}")
        ctx.misc["entity_linking"] = ctx.misc.get("entity_linking", []) + el_output
    except requests.exceptions.ConnectionError as exc:
        logger.warning(exc)
    return ctx


def get_wiki_parser_triplets(ctx: Context):
    try:
        el_output = ctx.misc.get("entity_linking", [[]])[-1]
        utterances = list(ctx.requests.values())
        parser_info = ["find_top_triplets"]
        if el_output:
            requested_data = {"parser_info": parser_info, "query": [el_output], "utt_num": len(utterances)}
            wp_output = requests.post(WIKI_PARSER_URL, json=requested_data).json()
            ctx.misc["wiki_parser"] = ctx.misc.get("wiki_parser", []) + wp_output
    except requests.exceptions.ConnectionError as exc:
        logger.warning(exc)
    return ctx
