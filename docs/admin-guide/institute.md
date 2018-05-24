## Institutes

Institutes are objects that group users and cases. Users belong to a institute and in this way permissions to view cases can be handeld. Cases are always "owned" by an institute and thereby grants acces for all users within that institute to view and work with a case. Cases can be shared with other institutes.

Institutes have a unique internal id and a display name that is what the users see when browsing. One or several users can be sanger recipients for a institute which means that when a user is pushing the button "Order Sanger" on the variant page an email is sent to all sanger recipients with relevant information, such as coordinates for a variant.

## Updating institutes

All variables except `'internal_id'` can be updated for a institute. 

Please run `scout update institute` for more information.