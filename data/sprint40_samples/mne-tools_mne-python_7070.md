# [MRG] Add spectro-spatial decomposition SSD example (#7070)
URL: https://github.com/mne-tools/mne-python/pull/7070
State: closed | PR: YES
Comments: 88 | Created: 2019-11-16T23:24:15Z | Closed: 2020-11-13T13:04:08Z

## Body (first 1000 chars)
This is a first example demonstrating spatial filtering with SSD (Nikulin et al 2011, NIMG), which essentially enhances the oscillatory signal of interest by removing background signal from surrounding frequencies.
The example is autonomous as is, but if we converge on ideas, I'd extend it to have a Transformer API like SPoC or CSP.

cc @agramfort @DavidSabbagh @pierreablin @wmvanvliet @britta-wstnr 

## Comments

--- Comment 1 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/mne-tools/mne-python/pull/7070?src=pr&el=h1) Report
> Merging [#7070](https://codecov.io/gh/mne-tools/mne-python/pull/7070?src=pr&el=desc) into [master](https://codecov.io/gh/mne-tools/mne-python/commit/ef7d7c1899911b821312cc5be1558cc2d6ae4816?src=pr&el=desc) will **decrease** coverage by `0.04%`.
> The diff coverage is `n/a`.


```diff
@@            Coverage Diff            @@
##           master   #7070      +/-   ##
=========================================
- Coverage   89.74%   89.7%   -0.05%     
=========================================
  Files         442     444       +2     
  Lines       77783   78981    +1198     
  Branches    12620   12674      +54     
=========================================
+ Hits        69807   70850    +1043     
- Misses       5167    5319     +152     
- Partials     2809    2812       +3
```




--- Comment 2 by dengemann ---
Some outputs:

![img1](https://user-images.githubusercontent.com/1908618/69000765-24ff7880-08d5-11ea-90bc-bb8561b41088.png)

![img2](https://user-images.githubusercontent.com/1908618/69000766-292b9600-08d5-11ea-8a4a-7a6cf7a539be.png)

![img3](https://user-images.githubusercontent.com/1908618/69000769-2cbf1d00-08d5-11ea-93c7-6719569ec196.png)


--- Comment 3 by agramfort ---
See you can make it embrace the same API as XDawn. Basically have a
transform for arrays and apply for instances. YOu would get filters and
patterns using LinearModel
https://mne.tools/stable/generated/mne.decoding.LinearModel.html#mne.decoding.LinearModel

>


--- Comment 4 by dengemann ---
Another option would be an ICA like api. Allowing for exploring components and handling artifact removal, whitening etc. 
You just use a different model to get filters.

This makes me also think that I should explore the alternative whitened eigenvalue problem to compute SSD. It should help us handling magnetometers and gradiometers.

> On 17 Nov 2019, at 16:36, Alexandre Gramfort <notifications@github.com> wrote:
> 
> See you can make it embrace the same API as XDawn. Basically have a
> transform for arrays and apply for instances. YOu would get filters and
> patterns using LinearModel
> https://mne.tools/stable/generated/mne.decoding.LinearModel.html#mne.decoding.LinearModel
> 
> >
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub, or unsubscribe.


--- Comment 5 by agramfort ---
yes ICA API is similar. fit, transform & apply methods with some plot
methods

>


--- Comment 6 by dengemann ---
@agramfort pushed first API draft, let me know what you think.

Todo:
- [ ] switch to whitenining implementation for multiple channels
- [ ] handle EEG vs MEG.
- [ ] consolidate API
- [ ] tests

--- Comment 7 by agramfort ---
so far so good https://16861-1301584-gh.circle-artifacts.com/0/dev/auto_examples/decoding/plot_ssd_spatial_filters.html#sphx-glr-auto-examples-decoding-plot-ssd-spatial-filters-py !

--- Comment 8 by dengemann ---
@britta-wstnr @wmvanvliet thank you for your review. Any thoughts on the proposed API?

--- Comment 9 by wmvanvliet ---
+1 for having a `.transform()` which takes an array and an `.apply()` that takes a Raw/Epochs/Evoked.

--- Comment 10 by dengemann ---
@wmvanvliet thoughts on apply semantics? It could be used to reconstruct sensor signal from selected components, be it the most or the least oscillatory. We also should have an apply_cov to filter cov matrices.

--- Comment 11 by wmvanvliet ---
Exactly. It could just act as a filter: put an Epochs object in, get an Epochs object out that was filtered for maximum oscillatory activity. Put a Covariance object in, get a Covariance object out (no need for an explicit  `apply_cov`)

--- Comment 12 by mmagnuski ---
Hi, if I understand it correctly this is the same GED that is used internally in common spatial pattern and that also has multiple other applications for EEG/MEG (see for example Mike X Cohen's publications on GED).
In that case I think it would be good to first have the basic object that does GED on two covariance matrices (and handles patterns, `.apply()` etc.) and only then use it for more specialized cases like the one here or CSP. 

--- Comment 13 by dengemann ---
Thank you @vpeterson for your review, I shall get back to you during this week. I have marked this PR as a potential candidate for our next release, hoping that we can merge a first version within the next 3 weeks.

--- Comment 14 by larsoner ---
Have any time for this @dengemann ? If not let's push to 0.22

--- Comment 15 by dengemann ---
Yes I will get to it this week.

> On 9 Sep 2020, at 16:25, Eric Larson <notifications@github.com> wrote:
> 
> ﻿
> Have any time for this @dengemann ? If not let's push to 0.22
> 
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub, or unsubscribe.


--- Comment 16 by dengemann ---
@vpeterson I rebased the pull request to allow us to continue working on this. Shall we give it another try to let you do a PR into this one? We can work through the necessary steps. It would be nice to give credit to your work through commits. I'd also have few discussion points regarding the code you have shared with me. 

--- Comment 17 by larsoner ---
Other than this PR things are looking on track for release tomorrow

--- Comment 18 by dengemann ---
Quick update!
Together with @vpeterson we have revamped and extended the proposed API:

- SSD uses now an array (2d, 3d) interface to be more compatible with sklearn
- This way it is possible to fit SSD based on Raw or Epochs
- With the same input data both lead to similar results.

Open points:

- [ ] See how we can get improve preprocessing of inputs. I am thinking of removing bad segments as we do in ICA, passing the info to the constructor to inform the covariance code about channel details and adding sensitivity for annotations
- [ ] Check out how filtering with epochs behaves as we use short epochs ... I feel there is some room for improvement and I feel the mne.Epochs.filter was doing a better job
- [ ] Add a decoding example to show SSD in action
- [ ] moving code to module and adding unit tests!


 @vpeterson I have granted you push access to my repository. You can now directly commit into this branch [with great power comes great responsibility ... or so]. 



--- Comment 19 by dengemann ---
@vpeterson can you run the current example on your machine and see a) if it is fast and b) you get roughly the same results when using Epochs/Raw [figure 1 VS 4]?

--- Comment 20 by dengemann ---
> Exactly. It could just act as a filter: put an Epochs object in, get an Epochs object out that was filtered for maximum oscillatory activity. Put a Covariance object in, get a Covariance object out (no need for an explicit `apply_cov`)

@vpeterson @wmvanvliet the way the code evolved in the meantime .transform just pushes the data into the SSD subspace, .apply reconstructs the instance data from the SSD subspace. Would that make sense as an API? I think it could fly.

--- END ---