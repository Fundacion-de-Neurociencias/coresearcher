# MRG: refactor PSD functions (#2710)
URL: https://github.com/mne-tools/mne-python/pull/2710
State: closed | PR: YES
Comments: 148 | Created: 2015-12-15T20:58:30Z | Closed: 2016-01-17T17:07:17Z

## Body (first 1000 chars)
This is a quick update that adds information to docstring so people know where to look for the under-the-hood PSD estimation. It also adds code to keep the estimated psd/frequencies with the object after the transform method is called.


## Comments

--- Comment 1 by jasmainak ---
I can't seem to see your commit. Did you update the `.rst` file only or did you add the output htmls to the commit as well?


--- Comment 2 by choldgraf ---
I added a `see also` section - let me know if that's what you means. Regarding creating the attributes, I'm not sure how to do it differently (unless I shouldn't do it at all)


--- Comment 3 by jasmainak ---
I think the convention for attributes is that you add it to the `fit` method, not to the `transform` method. And they end with an underscore. See here: http://scikit-learn.org/stable/tutorial/statistical_inference/settings.html#estimators-objects. _I think_ you can't add an attribute to a `transform` method.


--- Comment 4 by choldgraf ---
Ah I see what you were referring to. regarding underscores and such that totally makes sense. For putting it in `fit` vs `transform`, this object already handles that strangely already. The `fit` method currently does nothing, it only returns `self`...so I wasn't sure what to do there...


--- Comment 5 by jasmainak ---
For now, I'd say ... let's not add the attributes here. This calls for an update to the time-frequency module as we discussed here: https://github.com/mne-tools/mne-python/issues/2290


--- Comment 6 by larsoner ---
FYI you have a flake error


--- Comment 7 by choldgraf ---
I just spent 5 minutes looking for an anti-cornflakes meme on the internet, no luck. Instead I will focus on doing actual work...

It sounds like this PR will change a bit either way. It sounds like the best thing is to add epochs functionality to the `time_frequency` module, and then have this sklearn structure call that function instead.

So I guess the question is does this warrant its own function (e.g., `multitaper_psd_epochs`, or should it be added as a flag to `compute_epochs_psd`, e.g. `compute_epochs_psd(...kind='mt'...)`?


--- Comment 8 by jasmainak ---
I vote for a new argument called `method` which is string type. So, no new function.


--- Comment 9 by jasmainak ---
Also, please remember to update a couple of tests :)


--- Comment 10 by choldgraf ---
naturally :)

On Wed, Dec 16, 2015 at 11:36 AM, Mainak Jas notifications@github.com
wrote:

> Also, please remember to update a couple of tests :)
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/mne-tools/mne-python/pull/2710#issuecomment-165220493
> .


--- Comment 11 by agramfort ---
let us know when you did the necessary changes.


--- Comment 12 by choldgraf ---
will do - trying to finish a PR in h5io right now but I will try to get to
this soon thereafter

On Fri, Dec 18, 2015 at 2:11 PM, Alexandre Gramfort <
notifications@github.com> wrote:

> let us know when you did the necessary changes.
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/mne-tools/mne-python/pull/2710#issuecomment-165908755
> .


--- Comment 13 by choldgraf ---
OK there's a first step. I made 2 main changes:
1. Added a `method` kw to the compute_epoch_psd function, this lets you do either welch or multitaper psd estimation.
2. Added support for arrays instead of only Epochs objects. Since the PSDEstimator expects an array this would allow it to call this function instead of doing its own multitaper estimation. Let me know if that's over-reaching and we shouldn't add the code to support arrays...it just wasn't much extra effort...


--- Comment 14 by choldgraf ---
More updates - the PSDEstimator should now work using compute_epochs_psd so it's a pretty simple class at this point. Also fixed up the attribute creation etc. If these look reasonable then I'll make some tests as well...


--- Comment 15 by jasmainak ---
> Added support for arrays instead of only Epochs objects. Since the PSDEstimator expects an array this would allow it to call this function instead of doing its own multitaper estimation. Let me know if that's over-reaching and we shouldn't add the code to support arrays...it just wasn't much extra effort...

I noticed that you added a new argument `Fs` to support this. I would instead just support `epochs` object, but have a private function support the `Fs` + array + epochs. When you call it from `compute_psd_epochs`, it would call this private function with `epochs` and when you call it from the `PSDEstimator`, you would call this private function with `Fs` + array. I can't think of a good reason why you would want to support `compute_psd_epochs` for arrays in the public API. Even the name of the function has `epochs` in it :)


--- Comment 16 by jasmainak ---
@choldgraf thanks for making this contribution. Please go ahead and add the tests :)


--- Comment 17 by agramfort ---
you'll need to add tests + show the new method for psd estimation on epochs in an example.


--- Comment 18 by choldgraf ---
Added some tests and made miscellaneous changes that people mentioned above. Still no example but that will come next if people are happy w/ what's there.


--- Comment 19 by jasmainak ---
looks like you need to fix travis and appveyor


--- Comment 20 by jasmainak ---
@choldgraf looks like we have made progress :) I think if you just refactor some of the code for the private function and update an example, we should be good.


--- END ---