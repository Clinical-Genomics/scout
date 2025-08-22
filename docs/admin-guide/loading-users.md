# Loading Scout users

To load a user into scout use the command `scout load user`. A user has to:

- belong to an *institute*
- have a *name*
- have a *email adress*

An example could look like:

```bash
scout load user --institute-id cust000 --user-name "Clark Kent" --user-mail clark@mail.com
```

See `scout load user --help` or the [user guide user section](../user-guide/users.md) for more information.

---

## Managing users from the web interface

Since **Scout v4.104**, it is also possible for an **admin user** to add, edit, or remove users directly from the **general Users page** in the web interface.

> ⚠️ Note: This page is accessible via the global users page, accessible from the **top-left dropdown menu on the top bar** and the top level institutes overview sidebar menu. Do not confuse it with the **Users link on the institute level sidebar menu**, which only lists users for a specific institute.

<img width="393" height="267" alt="Image" src="https://github.com/user-attachments/assets/72b3f77a-f0de-4711-956a-aaf37a0eb667" />
