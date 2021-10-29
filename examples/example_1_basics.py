import logging
import os
from typing import Optional, Union

from dff.core.keywords import TRANSITIONS, RESPONSE
from dff.core import Context, Actor
import dff.conditions as cnd
import dff.transitions as trn
import requests
from nltk.tokenize import sent_tokenize

import condition as dm_cnd
from entity_detection import has_entities, entity_extraction, slot_filling
from generic_responses import generic_response_condition, generic_response_generate

SF_URL = os.getenv("SF_URL")
SFP_URL = os.getenv("SFP_URL")
MIDAS_URL = os.getenv("MIDAS_URL")
ENTITY_DETECTION_URL = os.getenv("ENTITY_DETECTION_URL")
ENTITY_LINKING_URL = os.getenv("ENTITY_LINKING_URL")
WIKI_PARSER_URL = os.getenv("WIKI_PARSER_URL")

logger = logging.getLogger(__name__)

# First of all, to create a dialog agent, we need to create a dialog script.
# Below, `plot` is the dialog script.
# A dialog script is a flow dictionary that can contain multiple plot .
# Plot are needed in order to divide a dialog into sub-dialogs and process them separately.
# For example, the separation can be tied to the topic of the dialog.
# In our example, there is one flow called greeting_flow.

# Inside each flow, we can describe a sub-dialog.
# Here we can also use keyword `LOCAL`, which we have considered in other examples.

# Flow describes a sub-dialog using linked nodes, each node has the keywords `RESPONSE` and `TRANSITIONS`.

# `RESPONSE` - contains the response that the dialog agent will return when transitioning to this node.
# `TRANSITIONS` - describes transitions from the current node to other nodes.
# `TRANSITIONS` are described in pairs:
#      - the node to which the agent will perform the transition
#      - the condition under which to make the transition
plot = {
    "greeting_flow": {
        "start_node": {  # This is an initial node, it doesn't need an `RESPONSE`
            RESPONSE: "",
            # TRANSITIONS: {"node1": cnd.exact_match("Hi")},  # If "Hi" == request of user then we make the transition
            TRANSITIONS: {"node1": cnd.all([dm_cnd.is_sf("Open.Give.Opinion"), dm_cnd.is_midas("pos_answer")])},
        },
        "node1": {
            RESPONSE: "Hi, how are you?",  # When the agent goes to node1, we return "Hi, how are you?"
            TRANSITIONS: {"node2": cnd.exact_match("i'm fine, how are you?")},
        },
        "node2": {
            RESPONSE: "Good. What do you want to talk about?",
            TRANSITIONS: {"node3": cnd.exact_match("Let's talk about music.")},
        },
        "node3": {
            RESPONSE: "Sorry, I can not talk about music now.",
            TRANSITIONS: {"node4": cnd.exact_match("Ok, goodbye.")},
        },
        "node4": {
            RESPONSE: "bye",
            TRANSITIONS: {"node1": cnd.exact_match("Hi")},
        },
        "fallback_node": {  # We get to this node if an error occurred while the agent was running
            RESPONSE: "Ooops",
            TRANSITIONS: {"node1": cnd.exact_match("Hi")},
        },
    },
}

plot_extended = {
    "greeting_flow": {
        "start_node": {  # This is an initial node, it doesn't need an `RESPONSE`
            RESPONSE: "",
            # TRANSITIONS: {"node1": cnd.exact_match("Hi")},  # If "Hi" == request of user then we make the transition
            TRANSITIONS: {"node1": cnd.all([dm_cnd.is_sf("Open.Give.Opinion"), dm_cnd.is_midas("pos_answer")])},
        },
        "node1": {
            RESPONSE: "Hi, how are you?",  # When the agent goes to node1, we return "Hi, how are you?"
            TRANSITIONS: {"node2": cnd.exact_match("i'm fine, how are you?")},
        },
        "node2": {
            RESPONSE: "Good. What do you want to talk about?",
            TRANSITIONS: {"node3": cnd.exact_match("Let's talk about music."),
                          ("generic_responses_flow", "generic_response"): generic_response_condition},
        },
        "node3": {
            PROCESSING: {1: entity_extraction("singer", "PERSON")},
            RESPONSE: "What is your favourite singer?",
            TRANSITIONS: {"node4": has_entities("PERSON")},
        },
        "node4": {
            PROCESSING: {1: slot_filling},
            RESPONSE: "I also like [singer] songs.",
            TRANSITIONS: {"node5": cnd.exact_match("Ok, goodbye.")},
        },
        "node5": {
            RESPONSE: "bye",
            TRANSITIONS: {"node1": cnd.exact_match("Hi")},
        },
        "fallback_node": {  # We get to this node if an error occurred while the agent was running
            RESPONSE: "Ooops",
            TRANSITIONS: {"node1": cnd.exact_match("Hi")},
        },
    },
    "generic_responses_flow": {
        "start_node": {
            RESPONSE: "",
            TRANSITIONS: {"generic_response": generic_response_condition},
        },
        "generic_response": {
            RESPONSE: generic_response_generate,
            TRANSITIONS: {trn.repeat(): generic_response_condition},
        }
    }
}

# An actor is an object that processes user input replicas and returns responses
# To create the actor, you need to pass the script of the dialogue `plot`
# And pass the initial node `start_node_label`
# and the node to which the actor will go in case of an error `fallback_node_label`
# If `fallback_node_label` is not set, then its value becomes equal to `start_node_label` by default
actor = Actor(
    plot,
    start_node_label=("greeting_flow", "start_node"),
    fallback_node_label=("greeting_flow", "fallback_node"),
)


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
    ctx.misc["speech_functions"] = ctx.misc.get("speech_functions", []) + speech_functions
    return ctx


def get_sfp(ctx: Context):
    last_sf = ctx.misc["speech_functions"][-1][-1]
    requested_data = [last_sf]
    sf_predictions = requests.post(SFP_URL, json=requested_data).json()
    ctx.misc["sf_predictions"] = ctx.misc.get("sf_predictions", []) + sf_predictions[-1][0]["prediction"]
    return ctx


def get_midas(ctx: Context):
    last_response = ctx.last_response if ctx.last_response else "hi"
    requested_data = {
        "dialogs": [{"human_utterances": [{"text": ctx.last_request}], "bot_utterances": [{"text": last_response}]}]
    }
    midas = requests.post(MIDAS_URL, json=requested_data).json()[0]
    ctx.misc["midas"] = ctx.misc.get("midas", []) + midas
    return ctx


def get_entities(ctx: Context):
    last_request = ctx.last_request if ctx.last_request else ""
    requested_data = {
        "last_utterances": [[last_request]]
    }
    entities = requests.post(ENTITY_DETECTION_URL, json=requested_data).json()[0]
    ctx.misc["entity_detection"] = ctx.misc.get("entity_detection", []) + entities
    return ctx


def get_entity_ids(ctx: Context):
    last_request = ctx.last_request if ctx.last_request else ""
    entities = ctx.misc.get("entities", [{}])[-1].get("entities", [])
    request_data = {"entity_substr": [entities], "template": [""], "context": [[last_request]]}
    el_output = requests.post(ENTITY_DETECTION_URL, json=requested_data).json()
    ctx.misc["entity_linking"] = ctx.misc.get("entity_linking", []) + el_output
    return ctx


def get_wiki_parser_triplets(ctx: Context):
    el_output = ctx.misc.get("entity_linking", [[]])[-1]
    utterances = list(ctx.requests.values())
    parser_info = ["find_top_triplets"]
    if el_output:
        request_data = {"parser_info": parser_info, "query": [el_output], "utt_num": len(utterances)}
        wp_output = requests.post(WIKI_PARSER_URL, json=requested_data).json()
        ctx.misc["wiki_parser"] = ctx.misc.get("wiki_parser", []) + wp_output
    return ctx


# turn_handler - a function is made for the convenience of working with an actor
def turn_handler(
    in_request: str,
    ctx: Union[Context, str, dict],
    actor: Actor,
    true_out_response: Optional[str] = None,
):
    # Context.cast - gets an object type of [Context, str, dict] returns an object type of Context
    ctx = Context.cast(ctx)

    # Add in current context a next request of user
    ctx.add_request(in_request)
    ctx = get_sf(ctx)
    ctx = get_midas(ctx)
    ctx = get_entities(ctx)

    # pass the context into actor and it returns updated context with actor response
    ctx = actor(ctx)
    # get last actor response from the context
    out_response = ctx.last_response
    # the next condition branching needs for testing
    if true_out_response is not None and true_out_response != out_response:
        raise Exception(f"{in_request=} -> true_out_response != out_response: {true_out_response} != {out_response}")
    else:
        logger.info(f"{in_request=} -> {out_response}")
    return out_response, ctx


# testing
testing_dialog = [
    ("Hi", "Hi, how are you?"),  # start_node -> node1
    ("i'm fine, how are you?", "Good. What do you want to talk about?"),  # node1 -> node2
    ("Let's talk about music.", "Sorry, I can not talk about music now."),  # node2 -> node3
    ("Ok, goodbye.", "bye"),  # node3 -> node4
    ("Hi", "Hi, how are you?"),  # node4 -> node1
    ("stop", "Ooops"),  # node1 -> fallback_node
    ("stop", "Ooops"),  # fallback_node -> fallback_node
    ("Hi", "Hi, how are you?"),  # fallback_node -> node1
    ("i'm fine, how are you?", "Good. What do you want to talk about?"),  # node1 -> node2
    ("Let's talk about music.", "Sorry, I can not talk about music now."),  # node2 -> node3
    ("Ok, goodbye.", "bye"),  # node3 -> node4
]


def run_test():
    ctx = {}
    for in_request, true_out_response in testing_dialog:
        _, ctx = turn_handler(in_request, ctx, actor, true_out_response=true_out_response)
    logger.info(ctx)


# interactive mode
def run_interactive_mode(actor):
    ctx = {}
    while True:
        in_request = input("type your answer: ")
        _, ctx = turn_handler(in_request, ctx, actor)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    run_test()
    run_interactive_mode(actor)

# %%
