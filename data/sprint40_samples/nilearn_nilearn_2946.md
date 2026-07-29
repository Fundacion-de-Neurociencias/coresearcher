# [NF] migrate package `load_confounds` main function `load_confounds` (#2946)
URL: https://github.com/nilearn/nilearn/pull/2946
State: closed | PR: YES
Comments: 44 | Created: 2021-09-07T03:17:59Z | Closed: 2021-10-12T08:03:32Z

## Body (first 1000 chars)
Start migrating `load_confounds` to nilearn (#2777) on behalf of all coauthors. 

* ADD base class `Confounds` and all helper functions
* ADD test data; taken from OpenNeuro ds000003
* ADD all tests associated with class `Confounds`

Few things still needs some discussions and/or changes:

- [x] add more detailed doc on the relationship with fMRIprep
- [x] the version of fMRIprep it supports
- [x] demo
- [x] Add unit test for some low level functions (compcor and scrubbing especially need this)
- [x] Remove test data that can be generated on the fly (such as empty files).
- [x] Raise warning related to fMRIprep version.
- [x] Remove PCA option.
- [x] Refactor `Confounds` into a function?
- [x] the name of module - how to make clear about the fMRIprep part, do we need to?
- [x] Bibliography
- [x] Test related to `signal.clean` psc standardization.


## Comments

--- Comment 1 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/2946?src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) Report
> Merging [#2946](https://codecov.io/gh/nilearn/nilearn/pull/2946?src=pr&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (6ff1f1b) into [main](https://codecov.io/gh/nilearn/nilearn/commit/f8a9c239681b64cc51791f103b93451e8685bda2?el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (f8a9c23) will **increase** coverage by `0.46%`.
> The diff coverage is `100.00%`.

[![Impacted file tree graph](https://codecov.io/gh/nilearn/nilearn/pull/2946/graphs/tree.svg?width=650&height=150&src=pr&token=KpYArSdyXv&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn)](https://codecov.io/gh/nilearn/nilearn/pull/2946?src=pr&el=tree&utm_medium=referral&utm_source=gi

--- Comment 2 by htwangtw ---
I have done some research on the minimal version of fMRIprep output we can support and added them to the existing docstrings. We can fully support everything from 1.4.X, and 1.2.X except `compcor`.

There are two aspect that I would like @NicolasGensollen to make an executive call on:
1. I can make sure some sanity checks on versions added to this PR, or as a separate one. I prefer to have it as a separate one but would like to see what you think  makes more sense.
2. Name of the module: `load_confounds` only works with fMRIprep outputs. The current name is potentially confusing. It can make user think this is for all kinds of confounds, rather than just for fMRIprep.
My idea is to put `load_confounds` under a directory called `fmriprep`, and import the `Confounds` like this:
```python3
from nilearn.fmriprep import Confounds
```
This can be a place for all potential future fmriprep helper functions. WDYT? cc @pbellec 

--- Comment 3 by tsalo ---
@htwangtw can the module work generally with BIDS derivatives (especially w.r.t. https://github.com/bids-standard/bids-specification/pull/519, which proposes rules that are probably what dictate fMRIPrep's derivatives)? I think a `nilearn.bids` would be preferable to a `nilearn.fmriprep`.

--- Comment 4 by htwangtw ---
@tsalo Thanks for bringing this up! 

I had a quick read through of BEP 012. From what I am aware, `load_confounds` fits well, as there is plan to adapt to new changes in `fMRIprep`. We have some of the very minimal file validity checks for now and it would be great to have it streamlined with BIDS in the future. `nilearn.bids` is a good idea.

--- Comment 5 by lunebellec ---
I feel like `nilearn.fmriprep` would be the most straightforward at the moment, and something that may need to be revisited if a 
more general set of `bids` helper gets developed for nilearn. 

Currently, the main use case for the confounds features is for fMRIprep users. I am not aware of software using the BIDS fMRI derivatives at the moment, and I am not sure that fMRIprep itself conforms to the standard, which is still a draft as far as I can tell. Also, BIDS is most commonly associated with raw data, and unless `nilearn` expands to offer tools to handle BIDS data (which would then overlap with `pybids`), I am not sure what other modules will live in `nilearn.bids`. 



--- Comment 6 by tsalo ---
@pbellec one motivation I have for `bids` over `fmriprep` is that I'm working on functions to write out BIDS derivatives for GLMs (also based on a draft instead of the real specification) in #2715. We've also discussed the need for lightweight BIDS querying tools so that nilearn doesn't need pybids as a dependency. Some of those tools may end up in nilearn (or [`pybids-light`](https://github.com/bids-standard/pybids-light), which could become a dependency).

--- Comment 7 by lunebellec ---
so if there is a push for a set of bids tools in nilearn, `nilearn.bids` sounds good. Then we may need to rename the strategy module something like `fmriprep_denoise.py` and expose the confound strategies directly through `nilearn.bids`. So users would type
``` 
from nilearn.bids import Scrubbing
``` 
Another option would be to have long and explicit class names, like what is done for the masker classes.
``` 
from nilearn.bids import FmriPrepScrubbing
``` 


--- Comment 8 by NicolasGensollen ---
Thanks for opening this @htwangtw ! :+1: 
I'll make a review tomorrow but it looks really good at first glance. 
I think it could be helpful to have some examples that we could use to test things a little bit (they will be useful for the docs at some point anyway). 
Concerning the name of the module, I think it should be explicit enough such that users aren't surprised by what is inside (we get this remark every now and then about `input_data` which could have been `maskers` for example).  
I'm also worried that if we have a `bids` module, then it would make sense to put all bids-related functionalities inside which could quickly get messy (not saying it would necessarily, just trying to think how it could go wrong...).

--- Comment 9 by htwangtw ---
I can certainly add an examples. We do have an existing demo jupyter notebook based on [a NiftiMasker example](https://nilearn.github.io/auto_examples/03_connectivity/plot_signal_extraction.html#sphx-glr-auto-examples-03-connectivity-plot-signal-extraction-py). It needs some updates but I can certainly put it somewhere.

--- Comment 10 by htwangtw ---
w.r.t. fmriprep vs BIDS -
I had a think about this today. For now we are happy with what `load_confounds` is doing - it's a one stop shop for users to use fMRIprep outputs in nilearn. With the predefined strategies, it would be even simpler. Thus I have a preference for my original proposal (fmriprep).

Moving load_confounds to part of BIDS integration can be some work down the line. It will be a while before BEP 012 get merged and applied to fMRIPrep. That's a lot of things to anticipate and address for now, and I cannot see the changes of BEP 012 coming in the immediate future. At the moment load_confounds is for fMRIprep rather than BIDS.

--- Comment 11 by htwangtw ---
Regarding the suggestion on adding tests to private functions, I am only going to do a selective set.
We have a full coverage in the [original `load_confounds` repo](https://app.codecov.io/gh/SIMEXP/load_confounds) through test the high level API that's exposed to the users.
I can think of a few things that can be benefited from dedicated unit test 
1. some edge cases for scrubbing ineracting with non-steady-state outliers (this is done)
2. compcor option parsing. This is anticipating the changes in fMRIprep on the [new anatomical compcor label in 21.0.0rc0](https://github.com/nipreps/fmriprep/pull/2523)
Other than that I think the existing tests are doing good. 

--- Comment 12 by NicolasGensollen ---
@htwangtw I just pushed a commit to your PR in which I propose to refactor a little bit some tests.
Let me know what you think, and feel free to delete it if you are not satisfied with the proposed changes.

--- Comment 13 by htwangtw ---
> @htwangtw I just pushed a commit to your PR in which I propose to refactor a little bit some tests.
> Let me know what you think, and feel free to delete it if you are not satisfied with the proposed changes.

Thanks for the refactoring @NicolasGensollen 
Parametrising tests made the test more concise. I like it. 

--- Comment 14 by NicolasGensollen ---
@htwangtw The documentation build error wasn't related to this PR. I pushed a fix earlier today, so if you merge master you should have the CI all green again. :heavy_check_mark: 

Concerning the design choice of having a class vs. functions for Confounds, I also feel like we don't really need the complexity of multiple classes inheriting from the `Confounds` base class as they seem to "only" redefine some of their attributes. I might be wrong, but it seems to me that they mostly provide handy constructors but do not implement additional specific logic. 

Maybe the best way to decide is to compare the two designs (I can have a go at refactoring this if you want). 
WDYT?

--- Comment 15 by htwangtw ---
> @htwangtw The documentation build error wasn't related to this PR. I pushed a fix earlier today, so if you merge master you should have the CI all green again. heavy_check_mark
> 
> Concerning the design choice of having a class vs. functions for Confounds, I also feel like we don't really need the complexity of multiple classes inheriting from the `Confounds` base class as they seem to "only" redefine some of their attributes. I might be wrong, but it seems to me that they mostly provide handy constructors but do not implement additional specific logic.
> 
> Maybe the best way to decide is to compare the two designs (I can have a go at refactoring this if you want).
> WDYT?

Looks like there's problem with full build still, but partial build is fine. 

Great timing! I was leaving this comment to the last. I have time and just started a local branch for the refectoring and will see how it goes.

--- Comment 16 by bthirion ---
> @htwangtw The documentation build error wasn't related to this PR. I pushed a fix earlier today, so if you merge master you should have the CI all green again. heavy_check_mark
> 
> Concerning the design choice of having a class vs. functions for Confounds, I also feel like we don't really need the complexity of multiple classes inheriting from the `Confounds` base class as they seem to "only" redefine some of their attributes. I might be wrong, but it seems to me that they mostly provide handy constructors but do not implement additional specific logic.
> 
> Maybe the best way to decide is to compare the two designs (I can have a go at refactoring this if you want).
> WDYT?

Could not agree more. Thx !

--- Comment 17 by htwangtw ---
@NicolasGensollen @bthirion I have refactored the code to function - was less work then I thought and not that much chance in the number of lines. 
`Confounds` is now replaced by`load_confounds`. 
Currently, only the function exposed to the user is `load_confounds`. I tried to get some of the function name and docs terminology more consistent. However I still find the module names a bit chaotic. For now I have:
```
from nilearn.load_confounds import load_confounds
```
Is this okay?
Please let me know if things are making sense! 

--- Comment 18 by NicolasGensollen ---
>Is this okay?
Please let me know if things are making sense!

The import will depend on the name we end up choosing but `from nilearn.load_confounds import load_confounds` makes sense to me.

Having only `load_confounds` public for now also makes sense. 
I believe other classes which were inheriting from `Confounds` will then become public functions calling `load_confounds` with some combinations of parameters, right?

--- Comment 19 by htwangtw ---
> I believe other classes which were inheriting from `Confounds` will then become public functions calling `load_confounds` with some combinations of parameters, right?

Yes. So it will be like:
```python
from nilearn.load_confounds import minimal
```
Function:
```python
from nilearn.load_confounds import load_confounds

def minimal(img_files, motion="full", wm_csf="basic", demean=True):
    strategy = ["high_pass", "motion", "wm_csf", "non_steady_state"]
    # some sanity checks here 
    return load_confounds(strategy=strategy, motion=motion, wm_csf=wm_csf, demean=demean)
```

--- Comment 20 by GaelVaroquaux ---
In terms of import path, I wonder whether it would not make sense put
this together with the maskers. I don't really like the name of the
modules where the maskers are based (I'm to blame).

Maybe an "io" module that groups the confounder loading and the maskers?

My 2 cents from the peanut gallery


--- END ---