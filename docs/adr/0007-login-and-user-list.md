# Login: one external authentication method per instance, authorization by Scout's user list

- **Status:** Accepted
- **Date:** 2025-03-21 (login refactor and Keycloak); LDAP since 4.8.0, Google since 4.2x
- **References:** #5315, #5331, #5337, #5493, #5719

## Context

Sites use different identity providers: Google, institutional LDAP or Keycloak and other OpenID
Connect providers. Scout also needs its own user records for institutes and roles.

## Decision

- `login()` (`scout/server/blueprints/login/views.py`) uses exactly one method, chosen by
  configuration in this order: LDAP, Google, Keycloak, then a plain email form.
- Every method ends in `validate_and_login_user`, which refuses anyone not already in the `user`
  collection. Authentication is the provider's job; authorization is membership in Scout's user
  list.
- Users are added with `scout load user` or from the admin users page.

## Consequences

- Login methods are mutually exclusive per instance.
- LDAP needs no group rules, and removing a user from Scout revokes access.
- The fallback email login has no password check and is only meant for demos and development.
- Why authorization by user list was originally chosen is not recorded; see
  [Login system](../admin-guide/login-system.md) for the current reasoning.
