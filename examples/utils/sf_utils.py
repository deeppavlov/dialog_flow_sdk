import logging
import random
import re

import nltk

import utils as common_utils


logger = logging.getLogger(__name__)

DIALOG_BEGINNING_START_CONFIDENCE = 0.98
DIALOG_BEGINNING_CONTINUE_CONFIDENCE = 0.9
DIALOG_BEGINNING_SHORT_ANSWER_CONFIDENCE = 0.98
MIDDLE_DIALOG_START_CONFIDENCE = 0.7
SUPER_CONFIDENCE = 1.0
HIGH_CONFIDENCE = 0.98


GENERIC_REACTION_TO_USER_SPEECH_FUNCTION = {
    "React.Rejoinder.Support.Track.Check": ["Pardon?", "I beg your pardon?", "Mhm ?", "Hm?", "What do you mean?"],
    "React.Rejoinder.Track.Check": ["Pardon?", "I beg your pardon?", "Mhm ?", "Hm?", "What do you mean?"],
    "React.Rejoinder.Support.Track.Confirm": [
        "Oh really?",
        "Oh yeah?",
        "Sure?",
        "Are you sure?",
        "Are you serious?",
        "Yeah",
    ],
    "React.Respond.Confront.Reply.Contradict": [
        "Oh definitely no",
        "No",
        "No way",
        "Absolutely not",
        "Not at all",
        "Nope",
        "Not really",
        "Hardly",
    ],
    "React.Respond.Reply.Contradict": [
        "Oh definitely no",
        "No",
        "No way",
        "Absolutely not",
        "Not at all",
        "Nope",
        "Not really",
        "Hardly",
    ],
    "React.Respond.Confront.Reply.Disawow": [
        "I doubt it. I really do.",
        "I don't know.",
        "I'm not sure",
        "Probably.",
        "I don't know if it's true",
    ],
    "React.Respond.Reply.Disawow": [
        "I doubt it. I really do.",
        "I don't know.",
        "I'm not sure",
        "Probably.",
        "I don't know if it's true",
    ],
    "React.Respond.Confront.Reply.Disagree": [
        "No",
        "Hunhunh.",
        "I don't agree with you",
        "I disagree",
        "I do not think so",
        "I hardly think so",
        "I can't agree with you",
    ],
    "React.Respond.Reply.Disagree": [
        "No",
        "Hunhunh.",
        "I don't agree with you",
        "I disagree",
        "I do not think so",
        "I hardly think so",
        "I can't agree with you",
    ],
    "React.Respond.Support.Reply.Affirm": [
        "Oh definitely.",
        "Yeah.",
        "Kind of.",
        "Unhunh",
        "Yeah I think so",
        "Really.",
        "Right.",
        "That's what it was.",
    ],
    "React.Respond.Support.Reply.Acknowledge": [
        "I knew that.",
        "I know.",
        "No doubts",
        "I know what you meant.",
        "Oh yeah.",
        "I see",
    ],
    "React.Respond.Reply.Acknowledge": [
        "I knew that.",
        "I know.",
        "No doubts",
        "I know what you meant.",
        "Oh yeah.",
        "I see",
    ],
    "React.Respond.Support.Reply.Agree": [
        "Oh that's right. That's right.",
        "Yep.",
        "Right.",
        "Sure",
        "Indeed",
        "I agree with you",
    ],
    "React.Respond.Reply.Agree": [
        "Oh that's right. That's right.",
        "Yep.",
        "Right.",
        "Sure",
        "Indeed",
        "I agree with you",
    ],
    "Sustain.Continue.Monitor": ["You know?", "Alright?", "Yeah?", "See?", "Right?"],
}


def get_speech_function(ctx):
    human_utterance = list(ctx.requests.values())[-1]
    sfs = ctx.misc.get("speech_functions", [""])[-1]
    phrases = nltk.sent_tokenize(human_utterance)

    sfunctions = {}
    i = 0
    for phrase in phrases:
        if len(sfs) > i:
            sfunctions[phrase] = sfs[i]
        i = i + 1

    return sfunctions


def get_speech_function_predictions(ctx):
    predicted_sfs = [ctx.misc.get("sf_predictions", [""])[-1]]
    logger.info(f"predicted_sfs {predicted_sfs}")
    return predicted_sfs


def filter_speech_function_predictions(predicted_sfs):
    filtered_sfs = [sf_item for sf_item in predicted_sfs if "Open" not in sf_item]
    return filtered_sfs


patterns_agree = [
    "Support.Reply.Accept",
    "Support.Reply.Agree",
    "Support.Reply.Comply",
    "Support.Reply.Acknowledge",
    "Support.Reply.Affirm",
]
agree_patterns_re = re.compile("(" + "|".join(patterns_agree) + ")", re.IGNORECASE)


def is_speech_function_agree(ctx):
    sf_type, sf_confidence = get_speech_function(ctx)
    flag = sf_type and bool(re.search(agree_patterns_re, sf_type))
    # fallback to yes/no intents
    annotated_human_utterance = {"text": ctx.last_request, "annotations": {"midas": ctx.misc["midas"][-1]}}
    flag = flag or common_utils.is_yes(annotated_human_utterance)

    return flag


patterns_disagree = [
    "Support.Reply.Decline",
    "Support.Reply.Disagree",
    "Support.Reply.Non-comply",
    "Support.Reply.Withold",
    "Support.Reply.Disawow",
    "Support.Reply.Conflict",
]
disagree_patterns_re = re.compile("(" + "|".join(patterns_disagree) + ")", re.IGNORECASE)


def is_speech_function_disagree(ctx):
    sf_type, sf_confidence = get_speech_function(ctx)
    flag = sf_type and bool(re.search(disagree_patterns_re, sf_type))
    # fallback to yes/no intents
    annotated_human_utterance = {"text": ctx.last_request, "annotations": {"midas": ctx.misc["midas"][-1]}}
    flag = flag or common_utils.is_no(annotated_human_utterance)

    return flag


patterns_express_opinion = [
    "Initiate.Give.Opinion",
]
express_opinion_patterns_re = re.compile("(" + "|".join(patterns_express_opinion) + ")", re.IGNORECASE)


def is_speech_function_express_opinion(ctx):
    sf_type, sf_confidence = get_speech_function(ctx)
    flag = sf_type and bool(re.search(express_opinion_patterns_re, sf_type))
    # fallback to MIDAS & CoBot
    annotated_human_utterance = {"text": ctx.last_request, "annotations": {"midas": ctx.misc["midas"][-1]}}
    flag = flag or common_utils.is_opinion_expression(annotated_human_utterance)
    # # fallback to CoBot intents
    flag = flag or common_utils.is_no(annotated_human_utterance)
    # bug check (sometimes opinion by MIDAS can be incorrectly detected in a simple yes/no answer from user)
    flag = (
        flag
        and not common_utils.is_no(annotated_human_utterance)
        and not common_utils.is_yes(annotated_human_utterance)
    )
    return flag


patterns_demand_opinion = [
    "Initiate.Demand.Opinion",
]
demand_opinion_patterns_re = re.compile("(" + "|".join(patterns_demand_opinion) + ")", re.IGNORECASE)


def is_speech_function_demand_opinion(ctx):
    annotated_human_utterance = {"text": ctx.last_request, "annotations": {"midas": ctx.misc["midas"][-1]}}
    sf_type, sf_confidence = get_speech_function(ctx)
    flag = sf_type and bool(re.search(demand_opinion_patterns_re, sf_type))
    # # fallback to CoBot & MIDAS intents
    flag = flag or common_utils.is_opinion_request(annotated_human_utterance)
    flag = flag or common_utils.is_no(annotated_human_utterance)
    # bug check (sometimes opinion by MIDAS can be incorrectly detected in a simple yes/no answer from user)
    flag = (
        flag
        and not common_utils.is_no(annotated_human_utterance)
        and not common_utils.is_yes(annotated_human_utterance)
    )
    return flag


def get_not_used_template(used_templates, all_templates, any_if_no_available=True, random_response=False):
    available = list(set(all_templates).difference(set(used_templates)))
    if available:
        if random_response:
            return random.choice(available)
        else:
            return available[0]
    elif any_if_no_available:
        if random_response:
            return random.choice(all_templates)
        else:
            return all_templates[0]
    else:
        return ""


def get_not_used_and_save_generic_response(proposed_sf, ctx, random_response):
    logger.info(f"Getting not yet used generic response for proposed speech function {proposed_sf}...")
    shared_memory = ctx.misc.get("shared_memory", {})
    last_responses = shared_memory.get(proposed_sf + "_last_responses", [])

    resp = get_not_used_template(
        used_templates=last_responses,
        all_templates=GENERIC_REACTION_TO_USER_SPEECH_FUNCTION[proposed_sf],
        random_response=random_response
    )

    used_resp = last_responses + [resp]
    shared_memory["last_responses"] = used_resp[-2:]
    ctx.misc["shared_memory"] = shared_memory
    return resp
