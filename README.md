# CodeReviewBot - IN DEVELOPMENT

## Motivation
It's very common situation that novice programmers want somebody to review their code.
But at the same time they are developing their apps for weeks and they do not use branches.

## How it works
This app is solution for this problem: it generates Pull Requests based on master branch
and returns link to application on https://github.com/DiscordCodeReviewBot/.
So basically it does not need any engagement from the user other than
providing name of the repository.

## How to use
Just open in browser link in the following format:

```strona/<user>/<repository>```

and wait until link is generated - it can take up to few minutes,
depending on the size of the repository
(the biggest one this script was tested was "pallets/flask" - it took around 5 minutes to generate)
I would not risk creating PR for bigger projects - it may take too long.

## Known issues
1. Sometimes Server error is raised. If this happens just retry creating PR.
