# [FIX] extend supported BIDS entities (#3525)
URL: https://github.com/nilearn/nilearn/pull/3525
State: closed | PR: YES
Comments: 23 | Created: 2023-02-21T07:57:44Z | Closed: 2023-03-29T08:52:08Z

## Body (first 1000 chars)
<!---
This is a suggested pull request template for nilearn.
It's designed to capture information we've found to be useful in reviewing pull requests.

If there is other information that would be helpful to include, please don't hesitate to add it!

Please make sure your pull request also follows the 
[contribution guidelines](https://nilearn.github.io/stable/development.html#contribution-guidelines) that
will be enforced during the review process.
-->

<!-- Please indicate after the # which issue you're closing with this PR.
This is helpful for the maintainers AND will magically close the issue when this
pull request is merged!
If the PR closes multiple issues, includes "closes" before each one is listed.
https://help.github.com/articles/closing-issues-using-keywords -->
Fixes #3524
Fixes #3029
Fixes #3585
Relates to #3068

<!-- Please give a brief overview of what has changed in the PR.
If you're not sure what to write, consider it a note to the maintainers to i

## Comments

--- Comment 1 by github-actions[bot] ---
👋 @Remi-Gau Thanks for creating a PR!

Until this PR is ready for review, you can include the [WIP] tag in its title, or leave it as a github draft.

Please make sure it is compliant  with our [contributing guidelines](https://nilearn.github.io/stable/development.html#contribution-guidelines). In particular, be sure it checks the boxes listed below.
- [x] PR has an interpretable title.
- [x] PR links to Github issue with mention `Closes #XXXX` (see our documentation on [PR structure](https://nilearn.github.io/stable/development.html#pr-structure))
- [x] Code is PEP8-compliant (see our documentation on [coding style](https://nilearn.github.io/stable/development.html#coding-style))
- [x] Changelog or what's new entry in `doc/changes/latest.rst` (see our documentation on [PR structure](https://nilearn.github.io/stable/development.html#pr-structure))
For new features:
- [ ] There is at least one unit test per new function / class  (see our documentation on [testing](https://nilearn.github.

--- Comment 2 by codecov[bot] ---
## [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/3525?src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) Report
> Merging [#3525](https://codecov.io/gh/nilearn/nilearn/pull/3525?src=pr&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (c0c3cbc) into [main](https://codecov.io/gh/nilearn/nilearn/commit/7d762ed7fdd3df39b8e84c75c2a75a75b6b3a95a?el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (7d762ed) will **increase** coverage by `0.08%`.
> The diff coverage is `94.69%`.

```diff
@@            Coverage Diff             @@
##             main    #3525      +/-   ##
==========================================
+ Coverage   91.40%   91.49%   +0.08%     
==========================================
  Files         133      133              
  Lines       15318    15453     +135     
  Branches     3179     320

--- Comment 3 by Remi-Gau ---
@kchawla-pi 

I am refactoring a lot of the code you wrote in here.

If you have time, can you have a first look before I polish this PR for final review?

--- Comment 4 by kchawla-pi ---
Yes, will do this weekend

--- Comment 5 by kchawla-pi ---
A few more comments. Most are minor. Your idea to refactor BIDS functions to its own module is important.

--- Comment 6 by kchawla-pi ---
Thanks @Remi-Gau I enjoyed reviewing after a long time!

--- Comment 7 by Remi-Gau ---
> Thanks @Remi-Gau I enjoyed reviewing after a long time!

thank YOU @kchawla-pi for the super thorough review!

--- Comment 8 by kchawla-pi ---
So what remains for the PR to be approved and merged?

--- Comment 9 by Remi-Gau ---
> So what remains for the PR to be approved and merged?

better if #3351 goes in first: merge conflicts should be easier to resolve

--- Comment 10 by Remi-Gau ---
TODO: refactor and simplify the bids dataset generation code.

It has grown too complicated

--- Comment 11 by Remi-Gau ---
> so far as I'm a bit short on time this week.

No worries: I know how to keep myself busy. :-)

> Mostly minor things. 

Thanks !

> I think this PR is good to discuss next week at the coredev meeting. Will you be able to attend? 

In theory yes.

> I think we need to hold off merging this until we make decisions about removing default values and type annotations among other things. Like for example if all the added private bids related functions should live in `first_level.py`

Makes sense






--- Comment 12 by Remi-Gau ---
TODO

Came across https://github.com/nilearn/nilearn/issues/2750

So it may be good to add a test for the bids dataset generation code: it is in a way tested by the [tests for get_bids_file](https://github.com/nilearn/nilearn/blob/a3e46391818b7a25a4ad6b7ba42e257fd4f2001a/nilearn/interfaces/tests/test_bids.py#LL23C4-L23C4) but I would prefer to not rely on nilearn code to test nilearn code.

--- Comment 13 by Remi-Gau ---
> add a test for the bids dataset generation code

done

--- Comment 14 by kchawla-pi ---
This PR is like a Game of Thrones season! I'm getting more excited as it gets towards the finale! 😁

--- Comment 15 by Remi-Gau ---
> This PR is like a Game of Thrones season! I'm getting more excited as it gets towards the finale! grin

Wait... Have you actually SEEN the last season of GoT? 
It was a like a mix between a 💩 show and 🚋 wreck... I kinda hope this PR ends better.

😉 

--- Comment 16 by ymzayek ---
Hi @Remi-Gau what is left to do on this one? I see that some type hints have been removed but not all of it? (like in `data_gen` and `test_data_gen` for example)

--- Comment 17 by Remi-Gau ---
> Hi @Remi-Gau what is left to do on this one? I see that some type hints have been removed but not all of it? (like in `data_gen` and `test_data_gen` for example)

ha. I think I removed them in the public function but I stopped.

Let me remove those too.

But if you do not see anything else then this is good to go for me.

--- Comment 18 by Remi-Gau ---
@ymzayek 
I removed type hints in https://github.com/nilearn/nilearn/pull/3525/commits/7a57a4d0f5aec0c74a60bdf5f858b25fef03076d

--- Comment 19 by ymzayek ---
Ok thanks!

> ha. I think I removed them in the public function but I stopped.

I realized we didn't make the distinction in the meeting in terms of using typing in public vs private functions or in tests (or did we?) but maybe we should've. Anyways since it will be discussed again in a few months we can keep that in mind.

This PR seems ready to me. I don't know if @kchawla-pi wanted to do a last run through; seems the reviews have been extensive so I think it can be merged

--- Comment 20 by kchawla-pi ---
I don't know if i can. I think we can merge.
BTW, why remove the typing annotations?

--- END ---