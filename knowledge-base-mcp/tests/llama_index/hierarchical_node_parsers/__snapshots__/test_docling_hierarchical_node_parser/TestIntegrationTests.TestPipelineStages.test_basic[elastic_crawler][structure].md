 : 0 - 35: # How to contribute elastic-crawler
 : 1 - 342: The `elastic-crawler` repository is a free and ope
 : 2 - 244: If you want to be rewarded for your contributions,
 : 3 - 598: - Reporting issues - Getting help Types of contrib
 : 4 - 19: ## Reporting issues
 : 5 - 63: If something is not working as expected, please op
 : 6 - 15: ## Getting help
 : 7 - 326: The Ingestion team at Elastic maintains this repos
 : 8 - 24: ## Types of contribution
 : 9 - 16: ### Enhancements
 : 10 - 62: Enhancements that can be done after your initial c
 : 11 - 216: 1. Ensure the backend meets performance requiremen
 : 12 - 111: ℹ️ Use-case specific customizations (as opposed to
 : 13 - 25: ## Contribution Checklist
 : 14 - 23: ### Acceptance criteria
 : 15 - 226: All patch changes should have a corresponding GitH
 : 16 - 34: ### Correct code/file organization
 : 17 - 452: Any contribution should follow established pattern
 : 18 - 56: If you are unsure of where a file/class should go 
 : 19 - 17: ### Log verbosity
 : 20 - 164: Logging is important to get insights on what's hap
 : 21 - 25: A few tips per log level:
 : 22 - 541: - CRITICAL (50) -- anything that stops the service
 : 23 - 11: ### Linting
 : 24 - 269: Code style is important in shared codebases, as it
 : 25 - 123: You can run the linter locally with `./script/bund
 : 26 - 11: ### Testing
 : 27 - 294: Tests not only verify and demonstrate that a new f
 : 28 - 66: Our goal is to maintain 92% test coverage for the 
 : 29 - 72: You can run the tests locally with `./script/bundl
 : 30 - 74: Be sure to read about our unit tests and integrati
 : 31 - 19: ### Backport labels
 : 32 - 106: Make sure to include the appropriate backport labe
 : 33 - 25: ## Pull Request Etiquette
 : 34 - 86: *this is copied and adapted from https://gist.gith
 : 35 - 42: ### Why do we use a Pull Request workflow?
 : 36 - 242: PRs are a great way of sharing information, and ca
 : 37 - 79: **Ultimately though, the primary reason we use PRs
 : 38 - 54: **the commits that are made to our code repositori
 : 39 - 221: Done well, the commits (and their attached message
 : 40 - 73: **Poor quality code can be refactored. A terrible 
 : 41 - 31: ### What constitutes a good PR?
 : 42 - 58: A good quality PR will have the following characte
 : 43 - 519: - It will be a complete piece of work that adds va
 : 44 - 108: A PR does not end at submission though. A code cha
 : 45 - 81: A good PR should be able to flow through a peer re
 : 46 - 46: #### Ensure there is a solid title and summary
 : 47 - 232: PRs are a Github workflow tool, so it's important 
 : 48 - 103: That said however, they are a very useful aid in e
 : 49 - 325: Ensure that your PR title is scannable. People wil
 : 50 - 36: #### Be explicit about the PR status
 : 51 - 163: If your PR is not fully ready yet for reviews, con
 : 52 - 89: Use the proper labels to help people understand yo
 : 53 - 32: #### Keep your branch up-to-date
 : 54 - 210: Unless there is a good reason not to rebase - typi
 : 55 - 18: #### Keep it small
 : 56 - 228: Try to only fix one issue or add one feature withi
 : 57 - 230: If you must submit a large PR, try to at least mak
 : 58 - 70: If you can rebase up a large PR into multiple smal
 : 59 - 26: ## Reviewing Pull Requests
 : 60 - 42: It's a reviewers responsibility to ensure:
 : 61 - 201: - Commit history is excellent - Good changes are p
 : 62 - 23: ### Keep the flow going
 : 63 - 200: Pull Requests are the fundamental unit of how we p
 : 64 - 217: As PRs clog up in the system, merges become more d
 : 65 - 297: There is a balance between flow and ensuring the q
 : 66 - 70: Any quality issue that will obviously result in a 
 : 67 - 24: ### We are all reviewers
 : 68 - 247: To make sure PRs flow through the system speedily,
 : 69 - 101: Hopefully with the above guidelines, we can all st
 : 70 - 268: NB: With this in mind - if you are the first to co
 : 71 - 105: There's no reason why multiple people cannot comme
 : 72 - 37: ### Don't add to the PR as a reviewer
 : 73 - 152: It's sometimes tempting to fix a bug in a PR yours
 : 74 - 113: If you do this, you are no longer the reviewer of 
 : 75 - 295: It is of course possible to find a new reviewer, b