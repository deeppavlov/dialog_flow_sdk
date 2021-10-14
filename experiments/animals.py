import logging
from typing import Optional, Union

from dff.core.keywords import TRANSITIONS, RESPONSE, PROCESSING, GLOBAL, MISC
from dff.core import Context, Actor
import dff.conditions as cnd
import condition as dm_cnd

import requests
from nltk.tokenize import sent_tokenize


URL = "http://0.0.0.0:8108/model"
MIDAS_URL = "http://0.0.0.0:8090/model"

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
flows = {
    GLOBAL: {
        TRANSITIONS: {},
        PROCESSING: {},
        RESPONSE: {},
        MISC: {}
    },
	"greeting_flow": {
		"start_node": {
                TRANSITIONS: {'greet_and_ask_about_pets': cnd.all([dm_cnd.is_sf("Open.Demand.Fact")])},
                PROCESSING: {},
                RESPONSE: "Hi %username%!",
                MISC: {"speech_functions": ["Open.Attend"]}
                },
		"fallback_node": {
                TRANSITIONS: {},
                PROCESSING: {},
                RESPONSE: "Ooops"
                },
		"greet_and_ask_about_pets": {
                TRANSITIONS: {'cool_and_clarify_which_pets': cnd.any(                    [                        cnd.any(                            [                                dm_cnd.is_sf("React.Respond.Support.Reply.Agree"),                                dm_cnd.is_sf("React.Respond.Support.Reply.Affirm")                            ]                        ),                         cnd.all(                            [                                dm_cnd.is_sf("React.Rejoinder"),                                 dm_cnd.is_midas("pos_answer")                            ]                        )                    ]), 'sad_and_say_about_pets': cnd.any(                        [                            dm_cnd.is_sf("React.Respond.Confront.Reply.Disagree"),                            cnd.all(                            [                                dm_cnd.is_sf("React.Rejoinder"),                                 dm_cnd.is_midas("neg_answer")                            ]                        )                    ])},
                PROCESSING: {},
                RESPONSE: "I'm fine. Jack, a friend of mine told me about their new cat, Lucy. She's so cuddlesome! Do you like pets?",
                MISC: {"speech_functions": ["React.Rejoinder.Support.Track.Clarify"]}
                },
		"cool_and_clarify_which_pets": {
                TRANSITIONS: {'tell_me_more_about_fav_pets': cnd.all([dm_cnd.is_sf("React.Rejoinder.Support.Response.Resolve")])},
                PROCESSING: {},
                RESPONSE: "Oh, cool! What animals do you like the most?",
                MISC: {"speech_functions": ["React.Rejoinder.Support.Track.Clarify"]}
                },
		"sad_and_say_about_pets": {
                TRANSITIONS: {},
                PROCESSING: {},
                RESPONSE: "Oh, that's sad! Why is it so?",
                MISC: {"speech_functions": ["React.Rejoinder.Support.Track.Clarify"]}
                },
		"tell_me_more_about_fav_pets": {
                TRANSITIONS: {},
                PROCESSING: {},
                RESPONSE: "That's rather lovely! I like them, too!",
                MISC: {"speech_functions": ["React.Respond.Support.Reply.Affirm"]}
                }
		},
	
}

# An actor is an object that processes user input replicas and returns responses
# To create the actor, you need to pass the script of the dialogue `plot`
# And pass the initial node `start_node_label`
# and the node to which the actor will go in case of an error `fallback_node_label`
# If `fallback_node_label` is not set, then its value becomes equal to `start_node_label` by default
actor = Actor(
    flows,
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
    speech_functions = requests.post(URL, json=requested_data).json()
    ctx.misc["speech_functions"] = ctx.misc.get("speech_functions", []) + speech_functions
    return ctx


def get_midas(ctx: Context):
    last_response = ctx.last_response if ctx.last_response else "hi"
    requested_data = {
        "dialogs": [{"human_utterances": [{"text": ctx.last_request}], "bot_utterances": [{"text": last_response}]}]
    }
    midas = requests.post(MIDAS_URL, json=requested_data).json()[0]
    ctx.misc["midas"] = ctx.misc.get("midas", []) + midas
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
    # adding logger!
    

    # Add in current context a next request of user
    ctx.add_request(in_request)
    ctx = get_sf(ctx)
    ctx = get_midas(ctx)
    logger.info(f"{ctx=}")
    # pass the context into actor and it returns updated context with actor response
    ctx = actor(ctx)
    # get last actor response from the context
    out_response = ctx.last_response
    # the next condition branching needs for testing
    if true_out_response is not None and true_out_response != out_response:
        raise Exception(f"{in_request=} -> true_out_response != out_response: {true_out_response} != {out_response}")
    else:
        logging.info(f"{in_request=} -> {out_response}")
    return out_response, ctx


# # testing
# testing_dialog = [
#     ("Hi", "Hi, how are you?"),  # start_node -> node1
#     ("i'm fine, how are you?", "Good. What do you want to talk about?"),  # node1 -> node2
#     ("Let's talk about music.", "Sorry, I can not talk about music now."),  # node2 -> node3
#     ("Ok, goodbye.", "bye"),  # node3 -> node4
#     ("Hi", "Hi, how are you?"),  # node4 -> node1
#     ("stop", "Ooops"),  # node1 -> fallback_node
#     ("stop", "Ooops"),  # fallback_node -> fallback_node
#     ("Hi", "Hi, how are you?"),  # fallback_node -> node1
#     ("i'm fine, how are you?", "Good. What do you want to talk about?"),  # node1 -> node2
#     ("Let's talk about music.", "Sorry, I can not talk about music now."),  # node2 -> node3
#     ("Ok, goodbye.", "bye"),  # node3 -> node4
# ]


# def run_test():
#     ctx = {}
#     for in_request, true_out_response in testing_dialog:
#         _, ctx = turn_handler(in_request, ctx, actor, true_out_response=true_out_response)


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
    # run_test()
    run_interactive_mode(actor)
