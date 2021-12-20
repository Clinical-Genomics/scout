import logging

from flask import current_app, flash

from scout.server.extensions import ldap_manager

LOG = logging.getLogger(__name__)


def ldap_authorized(userid, password):
    """Log in a LDAP user

    Args:
        userid(str): user id provided in ldap login form (usually and email)
        password(str): user passord provided in ldap loding form

    Returns:
        authorized(bool): True or False
    """
    authorized = False
    try:
        authorized = ldap_manager.authenticate(
            username=userid,
            password=password,
            base_dn=current_app.config.get("LDAP_BASE_DN") or current_app.config.get("LDAP_BINDDN"),
            attribute=current_app.config.get("LDAP_USER_LOGIN_ATTR")
            or current_app.config.get("LDAP_SEARCH_ATTR"),
        )
    except Exception as ex:
        flash(ex, "danger")

    return authorized


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
    )
