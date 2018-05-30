# Getting started with Scout
Scout is a web-based visualizer for VCF-files. It helps to manage multiple patient cases in a unified and intuitive interface. Users can collaborate with other clinicians sharing comments and findings across your team.


## Institutes, Cases, Variants
Scout has a few levels of abstraction to deal with the data it presents. [Institutes](institutes.md) contain multiple [cases](cases.md) and group [users](users.md) into teams. Cases are a unit that is analysed together, usually the same as a family or a tumor/normal sample - they all share a subset of called variants. Variants are individual genotype calls across a single case.

> [insert screenshot here]

A case is an interesting concept worth expanding on. Given the context of diagnosing a Mendelian disorder, a case represents the investigation of typically a single family and the quest to find a single disease causing mutation.

As such there are some added features that try to support this process:

- a case can be assigned to a user to delegate responsibility
- various variants can be pinned as worth looking at for the whole team
- a feed keeps track of any case related activity in one single place

A lot of time has been spent on the layout for the big list of variants as well as the single variant detail view. They are meant to give a quick overview to enable efficient scanning of the information. It is also in this direction they will evolve in the future.
