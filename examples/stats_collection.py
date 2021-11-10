import uuid
import random
import pathlib

import tqdm

from dff.core.keywords import RESPONSE, TRANSITIONS
from dff.core import Context, Actor
import dff.conditions as cnd

import dff_node_stats

LOCATION = pathlib.Path(__file__).parent.resolve()
stats_file = LOCATION / "stats.csv"
if stats_file.exists():
    stats_file.unlink()

transitions = {
    "root": {
        "start": [
            "hi",
            "i like animals",
            "let's talk about animals",
        ]
    },
    "animals": {
        "have_pets": ["yes"],
        "like_animals": ["yes"],
        "what_animal": ["bird", "dog"],
        "ask_about_breed": ["pereat", "bulldog", "i do not known"],
    },
    "news": {
        "what_news": ["science", "sport"],
        "ask_about_science": ["yes", "let's change the topic"],
        "science_news": ["ok", "let's change the topic"],
        "ask_about_sport": ["yes", "let's change the topic"],
        "sport_news": ["ok", "let's change the topic"],
    },
    "small_talk": {
        "ask_some_questions": [
            "fine",
            "let's talk about animals",
            "let's talk about news",
        ],
        "ask_talk_about": ["dog", "let's talk about news"],
    },
}
# a dialog script
plot = {
    "root": {
        "start": {
            RESPONSE: "Hi",
            TRANSITIONS: {
                ("small_talk", "ask_some_questions"): cnd.exact_match("hi"),
                ("animals", "have_pets"): cnd.exact_match("i like animals"),
                ("animals", "like_animals"): cnd.exact_match("let's talk about animals"),
                ("news", "what_news"): cnd.exact_match("let's talk about news"),
            },
        },
        "fallback": {RESPONSE: "Oops"},
    },
    "animals": {
        "have_pets": {RESPONSE: "do you have pets?", TRANSITIONS: {"what_animal": cnd.exact_match("yes")}},
        "like_animals": {RESPONSE: "do you like it?", TRANSITIONS: {"what_animal": cnd.exact_match("yes")}},
        "what_animal": {
            RESPONSE: "what animals do you have?",
            TRANSITIONS: {"ask_about_color": cnd.exact_match("bird"), "ask_about_breed": cnd.exact_match("dog")},
        },
        "ask_about_color": {RESPONSE: "what color is it"},
        "ask_about_breed": {
            RESPONSE: "what is this breed?",
            TRANSITIONS: {
                "ask_about_breed": cnd.exact_match("pereat"),
                "tell_fact_about_breed": cnd.exact_match("bulldog"),
                "ask_about_training": cnd.exact_match("i do not known"),
            },
        },
        "tell_fact_about_breed": {
            RESPONSE: "Bulldogs appeared in England as specialized bull-baiting dogs. ",
        },
        "ask_about_training": {RESPONSE: "Do you train your dog? "},
    },
    "news": {
        "what_news": {
            RESPONSE: "what kind of news do you prefer?",
            TRANSITIONS: {
                "ask_about_science": cnd.exact_match("science"),
                "ask_about_sport": cnd.exact_match("sport"),
            },
        },
        "ask_about_science": {
            RESPONSE: "i got news about science, do you want to hear?",
            TRANSITIONS: {
                "science_news": cnd.exact_match("yes"),
                ("small_talk", "ask_some_questions"): cnd.exact_match("let's change the topic"),
            },
        },
        "science_news": {
            RESPONSE: "This is science news",
            TRANSITIONS: {
                "what_news": cnd.exact_match("ok"),
                ("small_talk", "ask_some_questions"): cnd.exact_match("let's change the topic"),
            },
        },
        "ask_about_sport": {
            RESPONSE: "i got news about sport, do you want to hear?",
            TRANSITIONS: {
                "sport_news": cnd.exact_match("yes"),
                ("small_talk", "ask_some_questions"): cnd.exact_match("let's change the topic"),
            },
        },
        "sport_news": {
            RESPONSE: "This is sport news",
            TRANSITIONS: {
                "what_news": cnd.exact_match("ok"),
                ("small_talk", "ask_some_questions"): cnd.exact_match("let's change the topic"),
            },
        },
    },
    "small_talk": {
        "ask_some_questions": {
            RESPONSE: "how are you",
            TRANSITIONS: {
                "ask_talk_about": cnd.exact_match("fine"),
                ("animals", "like_animals"): cnd.exact_match("let's talk about animals"),
                ("news", "what_news"): cnd.exact_match("let's talk about news"),
            },
        },
        "ask_talk_about": {
            RESPONSE: "what do you want to talk about",
            TRANSITIONS: {
                ("animals", "like_animals"): cnd.exact_match("dog"),
                ("news", "what_news"): cnd.exact_match("let's talk about news"),
            },
        },
    },
}

actor = Actor(plot, start_label=("root", "start"), fallback_label=("root", "fallback"))
stats = dff_node_stats.Stats(csv_file=stats_file)
stats.update_actor_handlers(actor, auto_save=False)
ctxs = {}
for i in tqdm.tqdm(range(300)):
    for j in range(4):
        ctx = ctxs.get(j, Context(id=uuid.uuid4()))
        label = ctx.last_label if ctx.last_label else actor.fallback_label
        flow, node = label[:2]
        if [flow, node] == ["root", "fallback"]:
            ctx = Context()
            flow, node = ["root", "start"]
        answers = list(transitions.get(flow, {}).get(node, []))
        in_text = random.choice(answers) if answers else "go to fallback"
        ctx.add_request(in_text)
        ctx = actor(ctx)
        ctx.clear(hold_last_n_indexes=3)
        ctxs[j] = ctx
    if i % 50 == 0:
        stats.save()
