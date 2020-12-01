from scout.constants import USER_DEFAULT_TRACKS
from scout.models import User


def build_user(user_info):
    """Build a user object

    Args:
        user_info(dict): A dictionary with user information

    Returns:
        user_obj(scout.models.User)
    """
    try:
        email = user_info["email"]
    except KeyError as err:
        raise KeyError("A user has to have a email")

    try:
        name = user_info["name"]
    except KeyError as err:
        raise KeyError("A user has to have a name")

    user_obj = User(email=email, name=name, id=user_info.get("id"), igv_tracks=USER_DEFAULT_TRACKS)

    ##TODO check that these are on the correct format
    if "roles" in user_info:
        user_obj["roles"] = user_info["roles"]

    if "location" in user_info:
        user_obj["location"] = user_info["location"]

    if "institutes" in user_info:
        user_obj["institutes"] = user_info["institutes"]

    return user_obj
