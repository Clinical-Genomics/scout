## Monitoring Users' Activity with a Log File

To ensure security and improve functionality, Scout provides the ability to log user activities, including interactions and navigation. This feature helps enhance platform performance and maintain security.

By default, user activity logging is **disabled**. However, system administrators can enable this feature by setting the `USERS_ACTIVITY_LOG_PATH` parameter in the `config.py` file.

### Log File Configuration

The name of the log file is arbitrary, but ensure that the Scout software has the necessary permissions to write to the specified file path.

### Enabling User Activity Logging

Once the `USERS_ACTIVITY_LOG_PATH` parameter is set in the configuration file, all users will be automatically logged out. They will be required to log in again and must check a box indicating their consent for activity logging. Please note that **no user**—regardless of login method (LDAP/OAuth2)—can log in without agreeing to this.

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/f49cc0b5-dd6e-456b-8951-48d99f1ad352">

### Logged Information

The information logged includes:

- User email
- Date and time of activity
- Specific domain endpoints visited or actions performed

This logging ensures transparency and accountability while using the platform.
