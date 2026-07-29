# [ENH] Continuation of  Decoder:Metaestimator (#2000)
URL: https://github.com/nilearn/nilearn/pull/2000
State: closed | PR: YES
Comments: 60 | Created: 2019-04-16T14:14:01Z | Closed: 2020-02-26T15:12:40Z

## Body (first 1000 chars)
Following #698 .

## Comments

--- Comment 1 by KamalakerDadi ---
I would ask for documentation even though they are low-level functions/helper functions. It would help easy to follow for other contributors and reviewers.

Thanks!

--- Comment 2 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/2000?src=pr&el=h1) Report
> :exclamation: No coverage uploaded for pull request base (`master@3554aa4`). [Click here to learn what that means](https://docs.codecov.io/docs/error-reference#section-missing-base-commit).
> The diff coverage is `87.72%`.

[![Impacted file tree graph](https://codecov.io/gh/nilearn/nilearn/pull/2000/graphs/tree.svg?width=650&token=KpYArSdyXv&height=150&src=pr)](https://codecov.io/gh/nilearn/nilearn/pull/2000?src=pr&el=tree)

```diff
@@           Coverage Diff            @@
##             master   #2000   +/-   ##
========================================
  Coverage          ?   94.8%           
========================================
  Files             ?     139           
  Lines             ?   18143           
  Branches          ?       0           
========================================
  Hits              ?   17201           
  Misses            ?     942           
  Partials          ?       0

--- Comment 3 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/2000?src=pr&el=h1) Report
> Merging [#2000](https://codecov.io/gh/nilearn/nilearn/pull/2000?src=pr&el=desc) into [master](https://codecov.io/gh/nilearn/nilearn/commit/9835930f414180d43c2d3287dd6d94bad31a710a?src=pr&el=desc) will **decrease** coverage by `0.04%`.
> The diff coverage is `97.52%`.

[![Impacted file tree graph](https://codecov.io/gh/nilearn/nilearn/pull/2000/graphs/tree.svg?width=650&token=KpYArSdyXv&height=150&src=pr)](https://codecov.io/gh/nilearn/nilearn/pull/2000?src=pr&el=tree)

```diff
@@            Coverage Diff             @@
##           master    #2000      +/-   ##
==========================================
- Coverage   92.81%   92.77%   -0.05%     
==========================================
  Files         148      150       +2     
  Lines       19042    19405     +363     
  Branches     2296     2344      +48     
==========================================
+ Hits        17674    18003     +329     
- Mis

--- Comment 4 by tbng ---
More test cases have been added. I'm working on adapting the `plot_haxby_full_analysis.py` example from using `sklearn.linear_model.SVC` to `nilearn.decoding.Decoder`.

--- Comment 5 by thomasbazeille ---
Also can you add in the docs : 
- A mention of this new feature in nilearn/doc/whats_new.rst
- Your new class / public functions in the right module of nilearn/doc/modules/reference.rst

--- Comment 6 by tbng ---
@thomasbazeille has helped to add the test_parallel_fit function. I also adapt the `plot_haxby_full_analysis` example to have the decoder object.

--- Comment 7 by tbng ---
> Also can you add in the docs :
> 
>     * A mention of this new feature in nilearn/doc/whats_new.rst
> 
>     * Your new class / public functions in the right module of nilearn/doc/modules/reference.rst

Documentation added.

--- Comment 8 by GaelVaroquaux ---
https://ci.appveyor.com/project/nilearn-ci/nilearn/builds/23967360
check_scoring does not exist in scikit-learn until 0.20.

Unfortunately, that means that we need to add a function in nilearn._utils.fixes that is backports some of the functionality of check_scoring and use it if the version of sklearn is below 0.20

--- Comment 9 by kchawla-pi ---
Why not make skl 0.20 the minimum? This would be the ideal time to do it. It is compatible with Python3.5 as well.

--- Comment 10 by kchawla-pi ---
> Unfortunately, that means that we need to add a function in nilearn._utils.fixes that is backports some of the functionality of check_scoring and use it if the version of sklearn is below 0.20

A conditional import, if SKL < 0.20, use the backport else the built-in one?

--- Comment 11 by tbng ---
Fix for compability with 0.19 (`sklearn.metrics.check_scoring` only available after 0.20) added.

--- Comment 12 by tbng ---
The circleCI build fails because of failure in making 
https://github.com/nilearn/nilearn/blob/master/doc/building_blocks/manual_pipeline.rst#loading-non-image-data-experiment-description.

This is due to the change in examples/plot_decoding_tutorial.py (https://github.com/nilearn/nilearn/pull/2000/files#diff-53ca76dbe29bb868031f2f5b7f0270ca) which removes the usage of NiftyMasker (decoder object can use the mask file directly). The `.rst` file above refers to those deleted line in the example.

I'm changing the `manual_pipeline.rst` according to this. 

--- Comment 13 by tbng ---
@kchawla-pi The codecov tests fail, how should I investigate and improve on it?
@GaelVaroquaux I have fixed the issues you raise, those are good comments.

--- Comment 14 by kchawla-pi ---
It means the tests don't cover all code or all scenarios of the code.
Figure out the needed unit tests and write them.

On Mon, May 6, 2019, 17:59 Binh Nguyen <notifications@github.com> wrote:

> @kchawla-pi <https://github.com/kchawla-pi> The codecov tests fail, how
> should I investigate and improve on it?
> @GaelVaroquaux <https://github.com/GaelVaroquaux> I have fixed the issues
> you raise, those are good comments.
>
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub
> <https://github.com/nilearn/nilearn/pull/2000#issuecomment-489674443>, or mute
> the thread
> <https://github.com/notifications/unsubscribe-auth/AB6SXRBBO3LNHJEPWFXM45LPUBIW5ANCNFSM4HGJMVQQ>
> .
>


--- Comment 15 by kchawla-pi ---
Hey @tbng  the `BaseDecoder.fit()` method in `decoding/decoding.py` is super duper long and doing many things. It needs to be refactored into smaller private methods and unit tests written for them.

You have separated sections within the `fit` method using comments, explaining what that section is doing. That is a good indicator of the need for refactoring and a good place to start the process.

It might also help with CodeCov's unhappiness.

--- Comment 16 by tbng ---
@kchawla-pi Following your advice I refactored the decoder object. But the big jump in coverage comes from the fact that I forgot to include the binary classification test case. Adding it makes a really big difference. 

--- Comment 17 by kchawla-pi ---
> @kchawla-pi Following your advice I refactored the decoder object. But the big jump in coverage comes from the fact that I forgot to include the binary classification test case. Adding it makes a really big difference.

That's great! I thought the refactoring (and the subsequent unit tests you write) might also help with some code coverage. 
You are off to a good start. Once the refactoring of the fit method with their unit tests is complete, we will be that much closer. I would love to merge this before OHBM, name drop this feature and start getting feedback. Thanks a lot for doing this!

--- Comment 18 by tbng ---
I'm not sure why the commit message for change in `nilearn/decoding/decoder.py` does not appear, but here are the changes:

- Fixed formatting of printing messages to follow Python 3 convention.
- `BaseDecoder._check_estimator` now does not return `estimator` object, instead it just do a check to  see whether `BaseDecoder.estimator` is valid one or not. Also clearer warning message for this function in case users decide to use custom estimator.   

--- Comment 19 by jeromedockes ---
sorry! I had completely missed the "ensemble" aspect; that models fitted on each
cv fold are averaged. Indeed that justifies the custom cross-validation logic.


only for `Ridge`, and `RidgeClassifier`, use the "CV" estimators instead of
including their `alpha` in the parameter grid.


--- Comment 20 by jeromedockes ---
could you add a reference to FReM in the docstring?

--- END ---