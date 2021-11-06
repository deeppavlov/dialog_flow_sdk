import logging

from dff.core.keywords import TRANSITIONS, RESPONSE, PROCESSING
from dff.core import Actor
import dff.conditions as cnd
import dff.labels as lbl

from utils import condition as loc_cnd
from utils import common
from utils.entity_detection import has_entities, entity_extraction, slot_filling


logger = logging.getLogger(__name__)


plot_extended = {
    "greeting_flow": {
        "start_node": {  # This is an initial node, it doesn't need an `RESPONSE`
            RESPONSE: "",
            TRANSITIONS: {"node1": cnd.all([loc_cnd.is_sf("Open.Give.Opinion"), loc_cnd.is_midas("pos_answer")])},
        },
        "node1": {
            RESPONSE: "Hi, how are you?",  # When the agent goes to node1, we return "Hi, how are you?"
            TRANSITIONS: {"node2": cnd.exact_match("i'm fine, how are you?")},
        },
        "node2": {
            RESPONSE: "Good. What do you want to talk about?",
            TRANSITIONS: {
                "node3": cnd.exact_match("Let's talk about music.")
            },
        },
        "node3": {
            RESPONSE: "What is your favourite singer?",
            TRANSITIONS: {"node4": has_entities(["tags:person", "tags:videoname", "wiki:Q177220"])},
        },
        "node4": {
            PROCESSING: {
                1: entity_extraction(singer=["tags:person", "tags:videoname", "wiki:Q177220"]),
                2: slot_filling,
            },
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
