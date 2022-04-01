import datetime
import logging
from scout.constants import (VERBS_MAP)
from scout.utils.date import pretty_date
LOG = logging.getLogger(__name__)

"""Controller module for first webview.



### Chiara's idea

-----------------------------------------------------
Case 1
-----------------------------------------------------
Edited synopsis. Marked 3 variants as causative, unmarked 1 variant as causative. Dismissed 27 variants.


-----------------------------------------------------
Case 2
-----------------------------------------------------
Commented on case. Commented on 2 variants, requested Sanger for one variant. Sent 1 variant to MatchMaker.


-----------------------------------------------------
Case 3
-----------------------------------------------------
Requested rerun for the case




"""

{
    "acmg": "updated ACMG classification for",
    "add_case": "added case",
    "add_cohort": "updated cohort for",
    "add_phenotype": "added HPO term for",
    "archive": "archived",
    "assign": "was assigned to",
    "cancel_sanger": "cancelled sanger order for", 
    "cancer_tier": "updated cancer tier for",
    "check_case": "marked case as",
    "comment": "commented on",
    "comment_update": "updated a comment for",
    "dismiss_variant": "dismissed variant for",
    "filter_audit": "marked case audited with filter",
    "filter_stash": "stored a filter for",
    "manual_rank": "updated manual rank for",
    "mark_causative": "marked causative for",
    "mark_partial_causative": "mark partial causative for",
    "mme_add": "exported to Matchmaker patient",
    "mme_remove": "removed from Matchmaker patient",
    "mosaic_tags": "updated mosaic tags for",
    "open_research": "opened research mode for",
    "pin": "pinned variant",
    "remove_cohort": "removed cohort for",
    "remove_phenotype": "removed HPO term for",
    "remove_variants": "removed variants for",
    "rerun": "requested rerun of",
    "rerun_monitor": "requested rerun monitoring for",
    "rerun_unmonitor": "disabled rerun monitoring for",
    "reset_dismiss_all_variants": "reset all dismissed variants for",
    "reset_dismiss_variant": "reset dismissed variant status for",
    "reset_research": "canceled research mode request for",
    "sanger": "ordered sanger sequencing for",
    "share": "shared case with",
    "status": "updated the status for",
    "synopsis": "updated synopsis for",
    "unassign": "was unassigned from",
    "unmark_causative": "unmarked causative for",
    "unmark_partial_causative": "unmarked partial causative for",
    "unpin": "removed pinned variant",
    "unshare": "revoked access for",
    "update_case": "updated case",
    "update_case_group_ids": "updated case group ids for",
    "update_clinical_filter_hpo": "updated clinical filter HPO status for",
    "update_default_panels": "updated default panels for",
    "update_diagnosis": "updated diagnosis for",
    "update_individual": "updated individuals for",
    "update_sample": "updated sample data for",
    "validate": "marked validation status for",
}
v


def get_events_of_interest(store, user):
    """Read event database and compile a list of selected events of interest"""
    LOG.debug(f"User: {user.email}")
    event_list = get_events(user, store)

    
    LOG.debug(f"Events list: {event_list}")
    
    return "None"



def get_events(user, store):
    """ """
    events = list(store.user_events({'_id':user.email}))
    pairs = []
    
    for event in events:
        pairs.append((event['verb'], event['category']))

    pairs_ = count_pairs(pairs)
    sorted = sorted(list(pairs), cmp = compare)

    return events


def compare(verb_a, verb_b):
    return verb_index(verb_a) > verb_index(verb_b)


def verb_index(verb):
    """Return index of verb in VERBS_MAP"""
    retur list(VERBS_MAP).index(verb)

    

def count_pairs(pairs):
    """Count tuples
        Args:
            pairs list of tuples (verb, category)

        Returns:
            Dict where each key is a pair, the value is numnber of occurances
    """

    def count_pairs_aux(pairs, acc):
        if pairs == []:
            return acc
        head, *tail = pairs
        if head in acc:
            acc[head] += 1
        else:
            acc[head] = 1
        return count_pairs_aux(tail, acc)

    a = count_pairs_aux(pairs, {})
    print(f"GOT: {a}")
    return a
    




def count_event(event_list, event_name):
    """Counts occurences of event_name in event_list, returns tuple"""
    count = 0

    for event in event_list:
        if event == event_name:
            count += 1
    return (event_name, count)




def get_event(events):
    """Get events for user

    Args:
    * user(Dict)

    Returns:
    * List: list of events sorted newest first
    """
    for event in events:
        event_outp = {}
        event_outp['case'] = event['case']
        event_outp['category'] = event['category']
        event_outp['link'] = event['link']
        event_outp['subject'] = event['subject']
        event_outp['updated_at'] = event['updated_at']
        event_outp['verb'] = event['verb']
        event_list.append(event_outp)

    return sorted(event_list, key=lambda d: d['updated_at'], reverse=True)


def drop_uninteresting_events(event_list):
    """Drop events from list"""
    unintersting_verbs = []
    interesting_list = []
    for event in event_list:
        if event['verb'] not in unintersting_verbs:
            interesting_list.append(event)
    return interesting_list

    

def prepare_pretty(event_list):
    """Pretty print dates, truncate long lines, map single verbs into sentances"""
    for event in event_list:
        event['verb'] = VERBS_MAP.get(event['verb']).capitalize()
        event['updated_at'] = pretty_date(event['updated_at'])
        if len(event['subject']) > 25:
            event['subject'] = event['subject'][0:25]+"..."
