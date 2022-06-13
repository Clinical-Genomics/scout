This PR adds a functionality or fixes a bug.
OR
This PR marks a new Scout release. We apply semantic versioning. This is a major/minor/patch release for reasons.

<details>
<summary>Testing on cg-vm1 server (Clinical Genomics Stockholm)</summary>

**Prepare for testing**
1. Make sure the PR is pushed and available on [Docker Hub](https://hub.docker.com/repository/docker/clinicalgenomics/scout-server-stage)
1. Fist book your testing time using the paxa software installed on `hasta`:
 - Log in into hasta: `ssh <USER.NAME>@hasta.scilifelab.se`
 - Activate the staging environment with the command `us` (Use Stage)
 - Run the command `paxa` and follow the instructions. Make sure to specify scout-stage as the resource you request and the server cg-vm1 as server.
1. Log out from the hasta server.
1. `ssh <USER.NAME>@cg-vm1.scilifelab.se`
1. `sudo -iu hiseq.clinical`
1. `ssh localhost`
1. (optional) Find out which scout branch is currently deployed on cg-vm1: `podman ps`
1. Stop the service with current deployed branch: `systemctl --user stop scout.target`
1. Start the scout service with the branch to test: `systemctl --user start scout@<this_branch>`
1. Make sure the branch is deployed: `systemctl --user status scout.target`
1. After testing is done, log out from `cg-vm1` and log in again in the `hasta` server, repeat the `hasta` and `paxa` procedure, which will release the allocated resource (scout-stage) to be used for testing by other users.
</details>


**How to test**:
1. how to test it, possibly with real cases/data

**Expected outcome**:
The functionality should be working
Take a screenshot and attach or copy/paste the output.

**Review:**
- [ ] code approved by
- [ ] tests executed by
