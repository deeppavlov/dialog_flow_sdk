import re
from copy import deepcopy


MIDAS_SEMANTIC_LABELS = ['open_question_factual', 'open_question_opinion', 'open_question_personal',
                         'yes_no_question', 'clarifying_question', 'command', 'dev_command', 'appreciation',
                         'opinion', 'complaint', 'comment', 'statement', 'other_answers', 'pos_answer', 'neg_answer']
MIDAS_FUNCTIONAL_LABELS = ['abandon', 'nonsense', 'opening', 'closing', 'hold', 'back-channeling', 'uncertain',
                           'non_compliant', 'correction']

def join_sentences_in_or_pattern(sents):
    return r"(" + r"|".join(sents) + r")"


def get_intents(annotated_utterance, probs=False, default_probs=None, default_labels=None):
    """Function to get intents from particular annotator or all detected.

    Args:
        annotated_utterance: dictionary with annotated utterance
        probs: if False we return labels, otherwise we return probs
        default_probs, default_labels: default probabilities and labels we return
    Returns:
        list of intents
    """
    default_probs = {} if default_probs is None else default_probs
    default_labels = [] if default_labels is None else default_labels
    annotations = annotated_utterance.get("annotations", {})

    midas_intent_probs = annotations.get("midas", {})
    if isinstance(midas_intent_probs, dict) and midas_intent_probs:
        semantic_midas_probs = {k: v for k, v in midas_intent_probs.items() if k in MIDAS_SEMANTIC_LABELS}
        functional_midas_probs = {k: v for k, v in midas_intent_probs.items() if k in MIDAS_FUNCTIONAL_LABELS}
        if semantic_midas_probs:
            max_midas_semantic_prob = max(semantic_midas_probs.values())
        else:
            max_midas_semantic_prob = 0.0
        if functional_midas_probs:
            max_midas_functional_prob = max(functional_midas_probs.values())
        else:
            max_midas_functional_prob = 0.0

        midas_semantic_intent_labels = [k for k, v in semantic_midas_probs.items() if v == max_midas_semantic_prob]
        midas_functional_intent_labels = [
            k for k, v in functional_midas_probs.items() if v == max_midas_functional_prob
        ]
        midas_intent_labels = midas_semantic_intent_labels + midas_functional_intent_labels
    elif isinstance(midas_intent_probs, list):
        if midas_intent_probs:
            # now it's a list of dictionaries. length of list is n sentences
            midas_intent_labels = []
            for midas_sent_probs in midas_intent_probs:
                max_midas_sent_prob = max(midas_sent_probs.values())
                midas_intent_labels += [k for k, v in midas_sent_probs.items() if v == max_midas_sent_prob]
            _midas_intent_probs = deepcopy(midas_intent_probs)
            midas_intent_probs = {}
            class_names = list(set(sum([list(resp.keys()) for resp in _midas_intent_probs], [])))
            for class_name in class_names:
                max_proba = max([resp.get(class_name, 0.0) for resp in _midas_intent_probs])
                midas_intent_probs[class_name] = max_proba
        else:
            midas_intent_probs = {}
            midas_intent_labels = []
    else:
        midas_intent_labels = []
    answer_probs, answer_labels = midas_intent_probs, midas_intent_labels
    if probs:
        return answer_probs
    else:
        return answer_labels


yes_templates = re.compile(
    r"(\byes\b|\byup\b|\byep\b|\bsure\b|go ahead|\byeah\b|\bok\b|okay|^(kind of|kinda)\.?$|"
    r"^why not\.?$|^tell me\.?$|^i (agree|do|did|like|have|had|think so)\.?$)"
)


def is_yes(annotated_phrase):
    midas_yes_detected = "pos_answer" in get_intents(annotated_phrase, which="midas", probs=False)
    if midas_yes_detected or re.search(yes_templates, annotated_phrase.get("text", "").lower()):
        return True
    return False


no_templates = re.compile(r"(\bno\b|\bnot\b|no way|don't|no please|i disagree|^neither.?$)")
DONOTKNOW_LIKE = [r"(i )?(do not|don't) know", "you (choose|decide|pick up)", "no idea"]
DONOTKNOW_LIKE_PATTERN = re.compile(join_sentences_in_or_pattern(DONOTKNOW_LIKE), re.IGNORECASE)


def is_donot_know(annotated_phrase):
    if DONOTKNOW_LIKE_PATTERN.search(annotated_phrase.get("text", "")):
        return True
    return False


def is_no_intent(annotated_phrase):
    midas_no_detected = "neg_answer" in get_intents(annotated_phrase, which="midas", probs=False)
    is_not_idontknow = not is_donot_know(annotated_phrase)
    if midas_no_detected and is_not_idontknow:
        return True

    return False


def is_no(annotated_phrase):
    midas_no_detected = "neg_answer" in get_intents(annotated_phrase, which="midas", probs=False)
    user_phrase = annotated_phrase.get("text", "").lower().strip().replace(".", "")
    is_not_horrible = "horrible" != user_phrase
    no_regexp_detected = re.search(no_templates, annotated_phrase.get("text", "").lower())
    is_not_idontknow = not is_donot_know(annotated_phrase)
    _yes = is_yes(annotated_phrase)
    if is_not_horrible and (midas_no_detected or no_regexp_detected) and is_not_idontknow and not _yes:
        return True

    return False


def is_question(text):
    return "?" in text


def substitute_nonwords(text):
    return re.sub(r"\W+", " ", text).strip()


def get_intent_name(text):
    splitter = "#+#"
    if splitter not in text:
        return None
    intent_name = text.split(splitter)[-1]
    intent_name = re.sub(r"\W", " ", intent_name.lower()).strip()
    return intent_name


OPINION_REQUEST_PATTERN = re.compile(
    r"(don't|do not|not|are not|are|do)?\s?you\s"
    r"(like|dislike|adore|hate|love|believe|consider|get|know|taste|think|"
    r"recognize|sure|understand|feel|fond of|care for|fansy|appeal|suppose|"
    r"imagine|guess)",
    re.IGNORECASE,
)
OPINION_EXPRESSION_PATTERN = re.compile(
    r"\bi (don't|do not|not|am not|'m not|am|do)?\s?"
    r"(like|dislike|adore|hate|love|believe|consider|get|know|taste|think|"
    r"recognize|sure|understand|feel|fond of|care for|fansy|appeal|suppose|"
    r"imagine|guess)",
    re.IGNORECASE,
)


def is_opinion_request(annotated_utterance):
    intents = get_intents(annotated_utterance, which="all", probs=False)
    intent_detected = any([intent in intents for intent in ["Opinion_RequestIntent", "open_question_opinion"]])
    uttr_text = annotated_utterance.get("text", "")
    if intent_detected or (OPINION_REQUEST_PATTERN.search(uttr_text) and "?" in uttr_text):
        return True
    else:
        return False


def is_opinion_expression(annotated_utterance):
    all_intents = get_intents(annotated_utterance, which="all")
    intent_detected = any([intent in all_intents for intent in ["opinion", "Opinion_ExpressionIntent"]])
    uttr_text = annotated_utterance.get("text", "")
    if intent_detected or OPINION_EXPRESSION_PATTERN.search(uttr_text):
        return True
    else:
        return False
