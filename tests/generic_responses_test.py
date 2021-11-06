import logging

from examples.utils import common

from examples import generic_responses as test

# testing
testing_dialog = [
    ("Hi", "Hi, how are you?"),  # start_node -> node1
    ("I'm fine, square root of two times square root of three is square root of six is it?", "Yes"),  # node1 -> generic_response
    ("Ok", "Ooops"),  # generic_response -> fallback_node
]


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_test(test.actor, testing_dialog)
