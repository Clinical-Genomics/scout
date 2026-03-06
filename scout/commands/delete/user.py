import logging

import click
from flask import current_app, url_for
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("user", short_help="Delete a user")
@click.option("-m", "--mail", required=True)
@with_appcontext
def user(mail):
    """Delete a user from the database"""
    LOG.info("Running scout delete user")
    adapter = store
    user_obj = adapter.user(mail)
    if not user_obj:
        LOG.warning("User {0} could not be found in database".format(mail))
        return

    # Check if user has associated MatchMaker Exchange submissions
    mme_submitted_cases = adapter.user_mme_submissions(user_obj)
    if mme_submitted_cases:
        click.confirm(
            f"User can't be removed because MatchMaker Exchange submissions (n. cases={len(mme_submitted_cases)}) are associated to it. Reassign patients to another user?",
            abort=True,
        )
        new_contact_email = click.prompt(
            "Assign patients to user with email",
            type=str,
        )
        try:
            adapter.mme_reassign(mme_submitted_cases, new_contact_email)
        except Exception as ex:
            LOG.error(ex)
            return

    result = adapter.delete_user(mail)
    if result.deleted_count == 0:
        return
    click.echo(f"User was correctly removed from database.")
    # remove this user as assignee from any case where it is found
    assigned_cases = adapter.cases(assignee=mail)
    updated_cases = 0
    with current_app.test_request_context("/cases"):
        for case_obj in assigned_cases:
            institute_obj = adapter.institute(case_obj["owner"])
            link = url_for(
                "cases.case",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
            )
            inactivate_case = case_obj.get("status", "active") == "active" and case_obj[
                "assignees"
            ] == [mail]
            if adapter.unassign(institute_obj, case_obj, user_obj, link, inactivate_case):
                updated_cases += 1
    click.echo(f"User was removed as assignee from {updated_cases} case(s).")
