# Contributing to Prosody

First off, thank you for considering contributing to Prosody! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, [make one](https://github.com/loganthorneloe/prosody/issues/new)! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then [fork Prosody](https://github.com/loganthorneloe/prosody/fork) and create a branch with a descriptive name.

A good branch name would be (where issue #33 is the ticket you're working on):

```sh
git checkout -b 33-add-new-feature
```

## Get the test suite running

Make sure you're running the tests before you start making changes. This will help you to ensure that you haven't broken anything.

```sh
python -m pytest
```

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first :smile_cat:

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with Prosody's master branch:

```sh
git remote add upstream git@github.com:loganthorneloe/prosody.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 33-add-new-feature
git rebase master
git push --set-upstream origin 33-add-new-feature
```

Finally, go to GitHub and [make a Pull Request](https://github.com/loganthorneloe/prosody/compare) :D

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing and merging, check out this guide on [merging vs. rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing).

## Merging a PR (for maintainers)

A PR can only be merged by a maintainer if:

*   It is passing CI.
*   It has been approved by at least one maintainer.
*   It has no requested changes.
*   It is up to date with current master.

Any maintainer is allowed to merge a PR if all of these conditions are met.
