This PR adds a fix for the leaking coffee machine.

Contact: @your_github_user or email

**How to test**:
1. install on stage of the coffee machine: `bash servers/resources/coffee.selecta.se/update-cg-stage.sh fix-water-leak`
1. activate stage: `us`
1. run following command: `cg get coffee`

**Expected outcome**:
`cg` should be providing you with a progress report of your coffee making. The coffee machine should not be leaking.
Take a screenshot and attach or copy/paste the output.

**Review:**
- [ ] code approved by
- [ ] tests executed by
- [ ] "Merge and deploy" approved by
Thanks for filling in who performed the code review and the test!

This is patch|minor|major **version bump** because ...
