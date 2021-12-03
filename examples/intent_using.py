import logging
from dff.core.keywords import TRANSITIONS, RESPONSE
from dff.core import Actor
import dff.conditions as cnd

from utils import condition as loc_cnd
from utils import common

logger = logging.getLogger(__name__)


plot = {
    "greeting_flow": {
        "start_node": {
            RESPONSE: "",
            TRANSITIONS: {"node1": loc_cnd.is_intent("topic_switching")},
        },
        "node1": {
            RESPONSE: "What do you want to talk about?",
            TRANSITIONS: {"node2": loc_cnd.is_intent("lets_chat_about")},
        },
        "node2": {
            RESPONSE: "Ok, what do you want to know?",
            TRANSITIONS: {"node1": cnd.true()},
        },
    },
}

actor = Actor(plot, start_label=("greeting_flow", "start_node"))


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_interactive_mode(actor)
