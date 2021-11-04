import logging
import re
from typing import Optional, Tuple

from dff.core import Context, Actor, Node

logger = logging.getLogger(__name__)


def find_entity_by_types(wp_output, types_to_find, relations=None):
    found_entity_wp = ""
    found_types = []
    found_entity_triplets = {}
    types_to_find = set(types_to_find)
    if isinstance(wp_output, dict):
        all_entities_info = wp_output.get("entities_info", {})
        topic_skill_entities_info = wp_output.get("topic_skill_entities_info", {})
        for entities_info in [all_entities_info, topic_skill_entities_info]:
            for entity, triplets in entities_info.items():
                types = (
                    triplets.get("types", [])
                    + triplets.get("instance of", [])
                    + triplets.get("subclass of", [])
                    + triplets.get("types_2_hop", [])
                    + triplets.get("occupation", [])
                )
                type_ids = [elem for elem, label in types]
                inters = set(type_ids).intersection(types_to_find)
                # conf = triplets["conf"]
                pos = triplets.get("pos", 5)
                if inters and pos < 2:
                    found_entity_wp = entity
                    found_types = list(inters)
                    entity_triplets = {}
                    if relations:
                        for relation in relations:
                            objects_info = triplets.get(relation, [])
                            if objects_info:
                                objects = [obj[1] for obj in objects_info]
                                entity_triplets[relation] = objects
                    if entity_triplets:
                        found_entity_triplets[entity] = entity_triplets
                    break
    return found_entity_wp, found_types, found_entity_triplets


def extract_entity(ctx, entity_type):
    user_text = ctx.last_request
    entities = ctx.misc.get("entity_detection", [{}])[-1]
    wp_output = ctx.misc.get("wiki_parser", [{}])[-1]
    if entity_type.startswith("tags"):
        tag = entity_type.split("tags:")[1]
        nounphrases = entities.get("labelled_entities", [])
        for nounphr in nounphrases:
            nounphr_text = nounphr.get("text", "")
            nounphr_label = nounphr.get("label", "")
            if nounphr_label == tag:
                found_entity = nounphr_text
                return found_entity
    elif entity_type.startswith("wiki"):
        wp_type = entity_type.split("wiki:")[1]
        found_entity, *_ = find_entity_by_types(wp_output, [wp_type])
        if found_entity:
            return found_entity
    elif entity_type == "any_entity":
        if entities:
            return entities[0]
    else:
        res = re.findall(entity_type, user_text)
        if res:
            return res[0]
    return ""


def has_entities(entity_types):
    def has_entities_func(ctx: Context, actor: Actor, *args, **kwargs):
        flag = False
        if isinstance(entity_types, str):
            extracted_entity = extract_entity(ctx, entity_types)
            if extracted_entity:
                flag = True
        elif isinstance(entity_types, list):
            for entity_type in entity_types:
                extracted_entity = extract_entity(ctx, entity_type)
                if extracted_entity:
                    flag = True
                    break
        return flag

    return has_entities_func


def entity_extraction(**ent_kwargs):
    def entity_extraction_func(
        ctx: Context,
        actor: Actor,
        *args,
        **kwargs,
    ) -> Optional[Tuple[str, Node]]:
        shared_memory = ctx.misc.get("shared_memory", {})
        slot_values = shared_memory.get("slot_values", {})
        for slot_name, slot_types in ent_kwargs.items():
            if isinstance(slot_types, str):
                extracted_entity = extract_entity(ctx, slot_types)
                if extracted_entity:
                    slot_values[slot_name] = extracted_entity
                    shared_memory["slot_values"] = slot_values
                    ctx.misc["shared_memory"] = shared_memory
            elif isinstance(slot_types, list):
                for slot_type in slot_types:
                    extracted_entity = extract_entity(ctx, slot_type)
                    if extracted_entity:
                        slot_values[slot_name] = extracted_entity
                        shared_memory["slot_values"] = slot_values
                        ctx.misc["shared_memory"] = shared_memory
        return ctx

    return entity_extraction_func


def slot_filling(
    ctx: Context,
    actor: Actor,
    *args,
    **kwargs,
) -> Optional[Tuple[str, Node]]:
    processed_node = ctx.a_s.get("processed_node", ctx.a_s["next_node"])
    prev_response = processed_node.response
    slot_name = re.findall(r"\[(.*?)\]", prev_response)
    shared_memory = ctx.misc.get("shared_memory", {})
    slot_values = shared_memory.get("slot_values", {})
    if slot_name:
        slot_value = slot_values.get(slot_name[0], "")
        replace_str = "[" + slot_name[0] + "]"
        response = prev_response.replace(replace_str, slot_value)
    else:
        response = prev_response
    processed_node.response = response
    ctx.a_s["processed_node"] = processed_node
    return ctx
