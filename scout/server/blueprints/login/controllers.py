"""Code for login controllers"""

DETECTIVES = [
    "Dick Tracy",
    "Miss Marple",
    "Sherlock Holmes",
    "Dr. Watson",
    "Hercule Poirot",
    "Jules Maigret",
    "Inspector Morse",
    "Dexter Morgan",
    "Stella Gibson",
    "Dale Cooper",
    "Jessica Fletcher",
    "Inspector Closseau",
    "Columbo",
]


def event_rank(count):
    """Determine event ranking."""
    if count < 100:
        return "aspirant"
    if count < 1000:
        return "constable"
    if count < 4000:
        return "sergeant"
    if count < 12000:
        return "inspector"
    if count < 30000:
        return "superintendent"
    if count < 50000:
        return "commander"
    return "commissioner"


def users(store):
    """Display a list of all users and which institutes they belong to."""
    user_objs = list(store.users())
    total_events = sum([1 for event in store.user_events()])
    for user_obj in user_objs:
        user_institutes = user_obj.get("institutes")
        if user_institutes:
            user_obj["institutes"] = [store.institute(inst_id) for inst_id in user_institutes]
        else:
            user_obj["institutes"] = []
        user_obj["events"] = sum([1 for event in store.user_events(user_obj)])
        user_obj["events_rank"] = event_rank(user_obj["events"])
    return dict(
        users=sorted(user_objs, key=lambda user: -user["events"]),
        total_events=total_events,
    )
