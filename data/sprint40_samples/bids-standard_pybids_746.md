# RF: Use pathlib.Path internally when possible (#746)
URL: https://github.com/bids-standard/pybids/pull/746
State: closed | PR: YES
Comments: 10 | Created: 2021-06-08T19:35:27Z | Closed: 2021-08-20T17:56:24Z

## Body (first 1000 chars)
fixes #553

- Haven't touched any of the tests.
- `Layout.root` is now a property that returns `str(Layout._root)` and `type(Layout._root) == Path`
- `BIDSFile` has two new properties: `._path` and `._dirname` which return `Path` versions of `.path` and `.dirname` resp.
- Most of the changes are refactorings.
- Some of the changes changed return types but mostly for private functions.
- Some changes happened to public functions that nevertheless seemed to exist for internal use only, like `validation.validate_indexing_args`.
- Lots of the changes are of the type `os.path.isabs(f)` -> `Path(f).is_absolute()`. I assumed `switching everywhere` included things like this as well.

## Comments

--- Comment 1 by kalenkovich ---
> A few quick suggestions - will try to make more steps asap

Thank you, @oesteban! I'll be able to take a look at your suggestions over the weekend.

--- Comment 2 by kalenkovich ---
@oesteban, @effigies, please advise me on the correct workflow to follow. Should I have re-requested reviews from you guys once I answered your comments? Or, is everything ok as it is and you will simply come back to this later?

--- Comment 3 by adelavega ---
Thanks for your changes @kalenkovich. Time's been a bit limited to do maintenance on pybids. 

Looks to me like there's a few requested changes that are yet to be made. If so, go ahead and make those changes and we can re-review. 

--- Comment 4 by kalenkovich ---
> Thanks for your changes @kalenkovich. Time's been a bit limited to do maintenance on pybids.

Oh, sure! I was just confused as to what was going on and whether I was required to do something on my side to proceed. Guess I should have just waited a bit longer.

> Looks to me like there's a few requested changes that are yet to be made. If so, go ahead and make those changes and we can re-review.

I resolved the conversations where I explained why I didn't agree with the suggestions in a comment. I also added a few more commits. There is still one conversation about line 101 with which I don't know how to proceed.



--- Comment 5 by kalenkovich ---
And now some tests are failing. Switching this PR to draft until I deal with that.

--- Comment 6 by kalenkovich ---
> And now some tests are failing. Switching this PR to draft until I deal with that.

All good now! I shouldn't have committed vai GitHub without checking locally even though it was one line of code :flushed:

--- Comment 7 by effigies ---
I'll try to have a thorough read-through some time this week. This is too big for a quick review.

--- Comment 8 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/746?src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard) Report
> Merging [#746](https://codecov.io/gh/bids-standard/pybids/pull/746?src=pr&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard) (6b13953) into [master](https://codecov.io/gh/bids-standard/pybids/commit/c2221bce24a27819c4098d82a423fd8f9dc7af9d?el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard) (c2221bc) will **decrease** coverage by `0.05%`.
> The diff coverage is `85.47%`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/746/graphs/tree.svg?width=650&height=150&src=pr&token=0d39OR1fhx&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard)](https://codecov.io/gh/bids-standard/pybids/pull/746?src

--- Comment 9 by kalenkovich ---
> Overall looks fine. Can you merge `master` to get a coverage report?

I didn't read your comment carefully enough and rebased instead of merging. Hope it is ok.

--- Comment 10 by effigies ---
Rebase is totally fine.

--- END ---