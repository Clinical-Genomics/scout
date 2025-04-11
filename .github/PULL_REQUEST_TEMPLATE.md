This PR adds a functionality or fixes a bug.
OR
This PR marks a new Scout release. We apply semantic versioning. This is a major/minor/patch release for reasons.

<details>
<summary>Testing on cg-vm1 server (Clinical Genomics Stockholm)</summary>

**Prepare for testing**
1. Make sure the PR is pushed and available on [Docker Hub](https://hub.docker.com/repository/docker/clinicalgenomics/scout-server-stage)
1. Fist book your testing time using the Pax software available at [https://pax.scilifelab.se/](https://pax.scilifelab.se). The resource you are going to call dibs on is `scout-stage` and the server is `cg-vm1`.
1. `ssh <USER.NAME>@cg-vm1.scilifelab.se`
1. `sudo -iu hiseq.clinical`
1. `ssh localhost`
1. (optional) Find out which scout branch is currently deployed on cg-vm1: `podman ps`
1. Stop the service with current deployed branch: `systemctl --user stop scout@<name_of_currently_deployed_branch>`
1. Start the scout service with the branch to test: `systemctl --user start scout@<this_branch>`
1. Make sure the branch is deployed: `systemctl --user status scout.target`
1. After testing is done, repeat procedure at [https://pax.scilifelab.se/](https://pax.scilifelab.se), which will release the allocated resource (`scout-stage`) to be used for testing by other users.
</details>

<details>
<summary>Testing on hasta server (Clinical Genomics Stockholm)</summary>

**Prepare for testing**
1. `ssh <USER.NAME>@hasta.scilifelab.se`
1. Book your testing time using the Pax software. `us; paxa -u <user> -s hasta -r scout-stage`. You can also use the WSGI Pax app available at [https://pax.scilifelab.se/](https://pax.scilifelab.se).
1. (optional) Find out which scout branch is currently deployed on cg-vm1: `conda activate S_scout; pip freeze | grep scout-browser`
1. Deploy the branch to test: `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-tool-stage.sh -e S_scout -t scout -b <this_branch>`
1. Make sure the branch is deployed: `us; scout --version`
1. After testing is done, repeat the `paxa` procedure, which will release the allocated resource (`scout-stage`) to be used for testing by other users.
</details>


**How to test**:
1. how to test it, possibly with real cases/data

**Expected outcome**:
The functionality should be working
Take a screenshot and attach or copy/paste the output.

**Review:**
- [ ] code approved by
- [ ] tests executed by
