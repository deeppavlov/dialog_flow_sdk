import logging

from examples.utils import common

from examples import entity_detection as test

# testing
testing_dialog = [
    ("Hi", "Hi, how are you?"),  # start_node -> node1
    ("i'm fine, how are you?", "Good. What do you want to talk about?"),  # node1 -> node2
    ("Let's talk about music.", "What is your favourite singer?"),  # node2 -> node3
    ("Kurt Cobain.", "I also like kurt cobain songs."),  # node3 -> node4
    ("Ok, goodbye.", "bye"),  # node4 -> node5
]


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    common.run_test(test.actor, testing_dialog)
