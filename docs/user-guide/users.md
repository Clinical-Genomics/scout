#Users

A user represents an individual with access to all [cases](cases.md) that belongs to the same [institute(s)](institutes.md) that the user does. From the main menu in scout one can access a *users* page that displays all existing users in the scout instance and ranks them based on how many actions they have performed.

## Create a user

Users are created through the CLI with command `scout load user`. Please see the `--help` argument for more information.
Email is used as user identification. A user can be admin which means that they have access to all institutes in the instance.

Example:

```bash
>scout load user --user-mail john@doe.com --admin --institute-id cust000 --user-name "John Doe"
```

A user can also have access to multiple institutes without being admin.

Example:

```bash
>scout load user -m john@doe.com -i cust000 -i cust001 -u "John Doe"
```


## Delete a user

Users can be deleted from the CLI.

Example:

```bash
>scout delete user --mail john@doe.com
```

## Update a user

It is possible to update existing users from the command line. It is possible to add or remove admin rights and to add or remove access to institutes.

Examples:

**Give admin rights**

```bash
>scout update user -u john@doe.com --update-role admin
```

**Remove admin rights**

```bash
>scout update user -u john@doe.com --remove-admin
```

**Add access to institutes**

Institutes has to exist in database

```bash
>scout update user -u john@doe.com --add-institute cust003 --add-institute cust004
```

**Remove access from institutes**

```bash
>scout update user -u john@doe.com --remove-institute cust001 --remove-institute cust002
```
