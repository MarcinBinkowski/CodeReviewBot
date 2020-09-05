# CodeReviewBot

## Motivation
It's very common situation that novice programmers want somebody to review their code.
But at the same time they are developing their apps for weeks and they do not use branches.

## How it works
This app is solution for this problem: it generates Pull Requests based on master branch
and returns link to application on https://github.com/DiscordCodeReviewBot/.
So basically it does not need any engagement from the user other than
providing name of the repository.

## How to use
Add this bot to your discord server using this link:

https://discord.com/api/oauth2/authorize?client_id=751780836549984407&permissions=18432&scope=bot

and then you can use this bot with command:
```
!CodeReview <link_to_repository_on_github>
```

## Known issues
1. Sometimes Server error is raised. If this happens just retry creating PR.
