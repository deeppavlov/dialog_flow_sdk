import logging

from dff.core.keywords import TRANSITIONS, RESPONSE
from dff.core import Actor
import dff.conditions as cnd
import dff.labels as lbl

from utils import condition as loc_cnd
from utils import common
from utils.generic_responses import generic_response_condition, generic_response_generate


logger = logging.getLogger(__name__)


plot_extended = {
    "greeting_flow": {
        "start_node": {  # This is an initial node, it doesn't need an `RESPONSE`
            RESPONSE: "",
            TRANSITIONS: {"node1": cnd.all([loc_cnd.is_sf("Open.Give.Opinion"), loc_cnd.is_midas("pos_answer")])},
        },
        "node1": {
            RESPONSE: "Hi, how are you?",  # When the agent goes to node1, we return "Hi, how are you?"
            TRANSITIONS: {"node2": cnd.exact_match("i'm fine, how are you?"),
                          ("generic_responses_flow", "generic_response"): generic_response_condition,
            },
        },
        "node2": {
            RESPONSE: "Good. I'm glad that you are having a good time.",
            TRANSITIONS: {"node1": cnd.exact_match("Hi")},
        },
        "fallback_node": {  # We get to this node if an error occurred while the agent was running
            RESPONSE: "Ooops",
            TRANSITIONS: {"node1": cnd.exact_match("Hi")},
        }
    },
    "generic_responses_flow": {
        "start_node": {
            RESPONSE: "",
            TRANSITIONS: {"generic_response": generic_response_condition},
        },
        "generic_response": {
            RESPONSE: generic_response_generate,
            TRANSITIONS: {lbl.repeat(): generic_response_condition},
        },
    }
}

actor = Actor(
    plot_extended,
    start_label=("greeting_flow", "start_node"),
    fallback_label=("greeting_flow", "fallback_node"),
)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_interactive_mode(actor)

# %%
