import logging

from examples.utils import common

from examples import intent_using as test

# testing
testing_dialog = [
    ("tell me something else", "What do you want to talk about?"),  # start_node -> node1
    ("let's chat about you", "Ok, what do you want to know?"),  # node1 -> node2
]


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_test(test.actor, testing_dialog)
