## Matchmaker Exchange integration

Starting from Scout release 4.4 the software can be configured to send patient data to a Matchmaker Exchange server.
A Matchmaker server that is tested and known to work with Scout is [patientMatcher](https://github.com/northwestwitch/patientMatcher), but any server which implements the standard endpoints described in the [MME APIs](https://github.com/ga4gh/mme-apis) can in theory be connected as well. It is worth mentioning that when using a MME server different than patientMatcher you will be able to export patient data to to Matchmaker, but it is not guaranteed that you will be able to modify the submission at a later stage or view matching results into Scout.

### Basic configuration for MME integration
Edit scout config file adding the following parameters:
```
MME_ACCEPTS = 'application/vnd.ga4gh.matchmaker.v1.0+json'
MME_URL = 'base_url_of_MME_service'
MME_TOKEN = 'security_token_accepted_by_MME'
```

Note that in order to accept and process Scout requests there should be already a registered client in the MME server database with the same security token that Scout is going to provide when creating requests.  
Parameter MME_ACCEPTS is specific for patientMatcher integration and should probably be modified according to the MME server being used.  


### Modifying user roles to include Matchmaker Exchange submitter privilege
You can grant users the privilege to add patients to Matchmaker and review eventual matches by adding a MME submitter role to the user object. To do so, run the following command:
```bash
scout update user -r mme_submitter -u scout_user_id
```
a mme_submitter role will be added in this way to the list of roles of the user object in database.
