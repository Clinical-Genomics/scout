# Institutes

Scout was made as a centralized tool where multiple users from different customers could work against the same instance. 
Institutes is a way to separate sensitive information from the users. 
Each [case](cases.md) has to have a institute as owner.
A [user](users.md) belongs to an institute and in that way restricted to see only the cases owned by that institute. 
So one instance of scout can have one or many institutes. Each institute could be the owner of multiple cases and have 
multiple users attached. Each institute has to have a unique identifier, `institute_id`.