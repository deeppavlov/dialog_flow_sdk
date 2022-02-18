import logging
from typing import Optional, Union

from dff.core import Context, Actor
from .services import (
    get_sf,
    get_sfp,
    get_midas,
    get_entities,
    get_entity_ids,
    get_wiki_parser_triplets,
    get_intent_and_ext_sf,
)

logger = logging.getLogger(__name__)

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
    ctx = get_sfp(ctx)
    ctx = get_midas(ctx)
    ctx = get_entities(ctx)
    ctx = get_entity_ids(ctx)
    ctx = get_wiki_parser_triplets(ctx)
    ctx = get_intent_and_ext_sf(ctx)

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


def run_test(actor, testing_dialog):
    ctx = {}
    for in_request, true_out_response in testing_dialog:
        _, ctx = turn_handler(in_request, ctx, actor, true_out_response=true_out_response)
    logger.info(ctx)


# interactive mode
def run_interactive_mode(actor):
    ctx = {}
    while True:
        in_request = input("type your answer: ")
        out_response, ctx = turn_handler(in_request, ctx, actor)
        logger.info(f"bot: {out_response}")
