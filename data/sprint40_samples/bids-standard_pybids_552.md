# Adding write_derivative_description and the related test. (#552)
URL: https://github.com/bids-standard/pybids/pull/552
State: closed | PR: YES
Comments: 11 | Created: 2019-11-22T19:15:31Z | Closed: 2021-07-02T02:52:55Z

## Body (first 1000 chars)
Some minor changes like changing the use of ''' to """ for docstrings have been made to be more close to PEP8 compliance but I did not make these change across the whole project. I just did it in the files I was working with. I also changed the use of os.path to pathlib just because... well, pathlib is awesome. The added test passed using `pytest bids/tests/utils.py --verbose`.

## Comments

--- Comment 1 by christian-oreilly ---
Fixes #551

--- Comment 2 by christian-oreilly ---
@tyarkoni Just seen your message in #551 I'll move this code to bids/layout/utils.py

--- Comment 3 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/552?src=pr&el=h1) Report
> Merging [#552](https://codecov.io/gh/bids-standard/pybids/pull/552?src=pr&el=desc) into [master](https://codecov.io/gh/bids-standard/pybids/commit/24d2032020fd407e5bcbbbf20943726f48717574?src=pr&el=desc) will **decrease** coverage by `0.34%`.
> The diff coverage is `54.28%`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/552/graphs/tree.svg?width=650&token=0d39OR1fhx&height=150&src=pr)](https://codecov.io/gh/bids-standard/pybids/pull/552?src=pr&el=tree)

```diff
@@            Coverage Diff             @@
##           master     #552      +/-   ##
==========================================
- Coverage   82.97%   82.62%   -0.35%     
==========================================
  Files          23       24       +1     
  Lines        2966     2999      +33     
  Branches      749      760      +11     
==========================================
+ Hits         2461     2478

--- Comment 4 by tyarkoni ---
Looks like there are test failure related to the introduction of pathlib. Given that we're no longer supporting, Python 2, it definitely makes sense to finally take advantage of pathlib, but the tests need to pass on 3.5+.  Haven't dug into it yet to figure out what's going on, or why it's only failing on 3.5, but I suspect we might need to replace some of the `os.path` calls with pathlib. @christian-oreilly can you take a look and see if you can figure out what's going on? I'll open a separate issue for more general os.path --> pathlib replacement.

--- Comment 5 by effigies ---
In Python 3.6, os.path began accepting PathLikes. You can either find a Path equivalent, or just wrap with str() for now.

--- Comment 6 by christian-oreilly ---
This looks good to go if nobody has further comments.

--- Comment 7 by christian-oreilly ---
@effigies Unless there are still some issues here, could you please merge this PR?

--- Comment 8 by effigies ---
Hi @christian-oreilly, sorry, I've been meaning to get to this. I'll try to complete a review tomorrow.

--- Comment 9 by adelavega ---
bump. @christian-oreilly ?

--- Comment 10 by adelavega ---
@christian-oreilly this PR is stale. I'm going to close it but feel free to re-open if it's worth reconciling. 

--- Comment 11 by christian-oreilly ---
Alright with me @adelavega. I don't personally need this PR anymore so, life being what it is, it fell low in my always increasingly longer TODO list! Sorry about not following up on that. The proposed code remains available here if some people need it and I guess that if it becomes useful to other people, someone might want to push it all the way to the finish line at a later point. I'll re-open it and push it myself if I need it again down the line.

--- END ---