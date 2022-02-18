import logging

from dff.core.keywords import TRANSITIONS, RESPONSE, MISC
from dff.core import Actor
import dff.conditions as cnd

from utils import condition as loc_cnd
from utils import common


logger = logging.getLogger(__name__)

plot = {
    "greeting_flow": {
        "start_node": {
            TRANSITIONS: {"greet_and_ask_about_pets": cnd.all([loc_cnd.is_sf("Open.Demand.Fact")])},
            RESPONSE: "Hi %username%!",
            MISC: {"speech_functions": ["Open.Attend"]},
        },
        "fallback_node": {TRANSITIONS: {}, RESPONSE: "Ooops"},
        "greet_and_ask_about_pets": {
            TRANSITIONS: {
                "cool_and_clarify_which_pets": cnd.any(
                    [
                        cnd.any(
                            [
                                loc_cnd.is_sf("React.Respond.Support.Reply.Agree"),
                                loc_cnd.is_sf("React.Respond.Support.Reply.Affirm"),
                            ]
                        ),
                        cnd.all([loc_cnd.is_sf("React.Rejoinder"), loc_cnd.is_midas("pos_answer")]),
                    ]
                ),
                "sad_and_say_about_pets": cnd.any(
                    [
                        loc_cnd.is_sf("React.Respond.Confront.Reply.Disagree"),
                        cnd.all([loc_cnd.is_sf("React.Rejoinder"), loc_cnd.is_midas("neg_answer")]),
                    ]
                ),
            },
            RESPONSE: "I'm fine. Jack, a friend of mine told me about their new cat, Lucy. "
            "She's so cuddlesome! Do you like pets?",
            MISC: {"speech_functions": ["React.Rejoinder.Support.Track.Clarify"]},
        },
        "cool_and_clarify_which_pets": {
            TRANSITIONS: {
                "tell_me_more_about_fav_pets": cnd.all([loc_cnd.is_sf("React.Rejoinder.Support.Response.Resolve")])
            },
            RESPONSE: "Oh, cool! What animals do you like the most?",
            MISC: {"speech_functions": ["React.Rejoinder.Support.Track.Clarify"]},
        },
        "sad_and_say_about_pets": {
            TRANSITIONS: {},
            RESPONSE: "Oh, that's sad! Why is it so?",
            MISC: {"speech_functions": ["React.Rejoinder.Support.Track.Clarify"]},
        },
        "tell_me_more_about_fav_pets": {
            TRANSITIONS: {},
            RESPONSE: "That's rather lovely! I like them, too!",
            MISC: {"speech_functions": ["React.Respond.Support.Reply.Affirm"]},
        },
    },
}

actor = Actor(
    plot,
    start_label=("greeting_flow", "start_node"),
    fallback_label=("greeting_flow", "fallback_node"),
)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_interactive_mode(actor)
