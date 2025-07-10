 : 0 - 10648: # How to contribute elastic-crawler  The `elastic-
   : 1 - 35: # How to contribute elastic-crawler
   : 2 - 342: The `elastic-crawler` repository is a free and ope
   : 3 - 244: If you want to be rewarded for your contributions,
   : 4 - 598: - Reporting issues - Getting help Types of contrib
   : 5 - 84: ## Reporting issues  If something is not working a
   : 6 - 343: ## Getting help  The Ingestion team at Elastic mai
   : 7 - 437: ## Types of contribution  ### Enhancements  Enhanc
   : 8 - 2646: ## Contribution Checklist  ### Acceptance criteria
     : 9 - 25: ## Contribution Checklist
     : 10 - 251: ### Acceptance criteria  All patch changes should 
     : 11 - 546: ### Correct code/file organization  Any contributi
       : 12 - 34: ### Correct code/file organization
       : 13 - 452: Any contribution should follow established pattern
       : 14 - 56: If you are unsure of where a file/class should go 
     : 15 - 753: ### Log verbosity  Logging is important to get ins
       : 16 - 17: ### Log verbosity
       : 17 - 164: Logging is important to get insights on what's hap
       : 18 - 25: A few tips per log level:
       : 19 - 541: - CRITICAL (50) -- anything that stops the service
     : 20 - 407: ### Linting  Code style is important in shared cod
       : 21 - 11: ### Linting
       : 22 - 269: Code style is important in shared codebases, as it
       : 23 - 123: You can run the linter locally with `./script/bund
     : 24 - 525: ### Testing  Tests not only verify and demonstrate
       : 25 - 11: ### Testing
       : 26 - 294: Tests not only verify and demonstrate that a new f
       : 27 - 66: Our goal is to maintain 92% test coverage for the 
       : 28 - 72: You can run the tests locally with `./script/bundl
       : 29 - 74: Be sure to read about our unit tests and integrati
     : 30 - 127: ### Backport labels  Make sure to include the appr
   : 31 - 3451: ## Pull Request Etiquette  *this is copied and ada
     : 32 - 25: ## Pull Request Etiquette
     : 33 - 86: *this is copied and adapted from https://gist.gith
     : 34 - 721: ### Why do we use a Pull Request workflow?  PRs ar
       : 35 - 42: ### Why do we use a Pull Request workflow?
       : 36 - 242: PRs are a great way of sharing information, and ca
       : 37 - 79: **Ultimately though, the primary reason we use PRs
       : 38 - 54: **the commits that are made to our code repositori
       : 39 - 221: Done well, the commits (and their attached message
       : 40 - 73: **Poor quality code can be refactored. A terrible 
     : 41 - 2613: ### What constitutes a good PR?  A good quality PR
       : 42 - 31: ### What constitutes a good PR?
       : 43 - 58: A good quality PR will have the following characte
       : 44 - 519: - It will be a complete piece of work that adds va
       : 45 - 108: A PR does not end at submission though. A code cha
       : 46 - 81: A good PR should be able to flow through a peer re
       : 47 - 712: #### Ensure there is a solid title and summary  PR
         : 48 - 46: #### Ensure there is a solid title and summary
         : 49 - 232: PRs are a Github workflow tool, so it's important 
         : 50 - 103: That said however, they are a very useful aid in e
         : 51 - 325: Ensure that your PR title is scannable. People wil
       : 52 - 292: #### Be explicit about the PR status  If your PR i
         : 53 - 36: #### Be explicit about the PR status
         : 54 - 163: If your PR is not fully ready yet for reviews, con
         : 55 - 89: Use the proper labels to help people understand yo
       : 56 - 244: #### Keep your branch up-to-date  Unless there is 
       : 57 - 552: #### Keep it small  Try to only fix one issue or a
         : 58 - 18: #### Keep it small
         : 59 - 228: Try to only fix one issue or add one feature withi
         : 60 - 230: If you must submit a large PR, try to at least mak
         : 61 - 70: If you can rebase up a large PR into multiple smal
   : 62 - 2450: ## Reviewing Pull Requests  It's a reviewers respo
     : 63 - 26: ## Reviewing Pull Requests
     : 64 - 42: It's a reviewers responsibility to ensure:
     : 65 - 201: - Commit history is excellent - Good changes are p
     : 66 - 815: ### Keep the flow going  Pull Requests are the fun
       : 67 - 23: ### Keep the flow going
       : 68 - 200: Pull Requests are the fundamental unit of how we p
       : 69 - 217: As PRs clog up in the system, merges become more d
       : 70 - 297: There is a balance between flow and ensuring the q
       : 71 - 70: Any quality issue that will obviously result in a 
     : 72 - 753: ### We are all reviewers  To make sure PRs flow th
       : 73 - 24: ### We are all reviewers
       : 74 - 247: To make sure PRs flow through the system speedily,
       : 75 - 101: Hopefully with the above guidelines, we can all st
       : 76 - 268: NB: With this in mind - if you are the first to co
       : 77 - 105: There's no reason why multiple people cannot comme
     : 78 - 603: ### Don't add to the PR as a reviewer  It's someti
       : 79 - 37: ### Don't add to the PR as a reviewer
       : 80 - 152: It's sometimes tempting to fix a bug in a PR yours
       : 81 - 113: If you do this, you are no longer the reviewer of 
       : 82 - 295: It is of course possible to find a new reviewer, b