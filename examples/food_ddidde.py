import logging

from df_engine.core.keywords import TRANSITIONS, RESPONSE, MISC, PROCESSING
from df_engine.core import Actor
import df_engine.conditions as cnd

from utils import condition as dm_cnd
from utils import common
from utils.entity_detection import has_entities, entity_extraction, slot_filling


logger = logging.getLogger(__name__)

plot = {
    "food_flow": {
        "start_node": {
            TRANSITIONS: {},
            RESPONSE: "",
            MISC: {"speech_functions": ["Open.Attend"]},
        },
        "fallback_node": {
            TRANSITIONS: {},
            RESPONSE: "Ooops",
            MISC: {"speech_functions": ["fallback_node"]}
        },
    },
}

actor = Actor(
    plot,
    start_label=("food_flow", "start_node"),
    fallback_label=("food_flow", "fallback_node"),
)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_interactive_mode(actor)