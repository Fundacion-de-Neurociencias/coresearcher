# ENH: Dynamically update convolution sampling rate for short duration events (#356)
URL: https://github.com/bids-standard/pybids/pull/356
State: closed | PR: YES
Comments: 54 | Created: 2019-01-25T17:04:32Z | Closed: 2019-03-11T18:24:42Z

## Body (first 1000 chars)
Fixes #354.

## Comments (first 1000 chars each)

--- Comment 1 by effigies ---
This might actually be spec-breaking... But it is so much faster than running `ToDense` and then `Convolve`. I have no idea why.

--- Comment 2 by tyarkoni ---
Probably because the default collection sampling rate is set to 10 Hz to avoid loss of information until the user's ready to downsample for output. Assuming you're passing in something closer to the TR, the arrays are going to be much smaller. This is *probably* okay for `Convolve` because the user probably isn't doing any further transformation after this, but it might still be worth eyeballing the convolved regressors to make sure that they look passably close to what you'd get with the default (upsampled) `sampling_rate`.

--- Comment 3 by adelavega ---
Makes sense to me to have this accesible from `Convolve`, but (i think) your original issue might have to due with the oversampling rate (hard coded in `compute_regressor`). I set that to `50`, but perhaps tweaking that higher would lead to proper convolution.

Should we also make that parameter accessible?

--- Comment 4 by tyarkoni ---
Oh, also, at one point there was a really nasty bug where the sampling rate was effectively interacting with the HRF convolution code's `oversampling` parameter. I believe that's been fixed in nistats, but definitely plot the regressors for a dataset or two before we merge this. (Also, yes, I believe this does break spec—and I don't think we can update the spec to include a sampling_rate parameter, as it's not so intuitive why that would be relevant at the convolution stage as opposed to any other transformation.)

--- Comment 5 by tyarkoni ---
Actually, I'm not sure I see the need for this PR. If you call `ToDense` before `Convolve`, passing the same `sr`, doesn't that also speed up to the same degree? I'm guessing it's just the difference between what you're passing in, and what the default value is...

--- Comment 6 by tyarkoni ---
@adelavega I don't think we should expose oversampling as a transformation parameter. But we probably need to adjust it on-the-fly based on the minimum duration of encountered events. (This will unfortunately make processing very slow for such events, but I don't see any way around that short of the user deciding to explicitly downsample ahead of time, which will throw away information and may produce fairly diffferent regressors in some cases.)

--- Comment 7 by adelavega ---
Definitely check your regressors. I'm a bit surprised its happening with oversampling set at 50 though. 

I think I'm convinced there's no need to expose either one of them at the level of the spec API. If its slower to call `ToDense` before Convolve, that seems like an implementational issue. 

@effigies can you try tweaking oversampling higher (~100?), and see if that at least prevents the zeroing out. If so we can then implement a heuristic for setting that parameter, and maybe if it continue to be a problem allow this to be set through `config`

--- Comment 8 by adelavega ---
Oh, I see the event durations were less than `1/50`. Then its definitely due to oversampling, and we can use the shortest event duration to set the oversampling rate. 

Also, to be clear I don't think it was ever fixed in nistats, I simply convinced them to expose the parameter & set the default value 50. 

--- Comment 9 by effigies ---
> Actually, I'm not sure I see the need for this PR. If you call `ToDense` before `Convolve`, passing the same `sr`, doesn't that also speed up to the same degree? I'm guessing it's just the difference between what you're passing in, and what the default value is...

No. Again, no idea why. If I do `ToDense(sampling_rate=200) -> Convolve()`, I have yet to have the patience to wait for it to finish (on a single variable). `Convolve(sampling_rate=200)` with this patch is fast.

--- Comment 10 by effigies ---
Okay, it may be that this isn't working anyway...

--- Comment 11 by effigies ---
LOL, I wasn't actually calling `sampling_rate`. Hence the speedup.

Anyway, to get down to the actual, better solution, we'll need a consistent sampling rate across all variables. However from what I can tell, the `_transform()` method only gets one variable at a time, and if there are any differences in the shortest duration, we're not going to get results of the same length.

Do you have any thoughts on the best way to find a sensible sampling rate? Or is setting the oversampling rate on a per-variable basis okay, since it will all get down-sampled back to the collection-level SR?

--- Comment 12 by tyarkoni ---
I don't think there's a problem setting different sampling rates for each variable. They all get resampled to the same resolution at output (i.e., when you call `get_design_matrix`) if needed. So it's probably most efficient computationally to only increase oversampling for variables that need it.

--- Comment 13 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/356?src=pr&el=h1) Report
> Merging [#356](https://codecov.io/gh/bids-standard/pybids/pull/356?src=pr&el=desc) into [master](https://codecov.io/gh/bids-standard/pybids/commit/e9fc2df43d560b75190f4e4cb6300f8ba5442a2b?src=pr&el=desc) will **not change** coverage.
> The diff coverage is `100%`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/356/graphs/tree.svg?width=650&token=0d39OR1fhx&height=150&src=pr)](https://codecov.io/gh/bids-standard/pybids/pull/356?src=pr&el=tree)

```diff
@@           Coverage Diff           @@
##           master     #356   +/-   ##
=======================================
  Coverage   73.27%   73.27%           
=======================================
  Files          24       24           
  Lines        2604     2604           
  Branches      640      640           
=======================================
  Hits         1908     1908           
  Misses        513      5

--- Comment 14 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/356?src=pr&el=h1) Report
> Merging [#356](https://codecov.io/gh/bids-standard/pybids/pull/356?src=pr&el=desc) into [master](https://codecov.io/gh/bids-standard/pybids/commit/e9fc2df43d560b75190f4e4cb6300f8ba5442a2b?src=pr&el=desc) will **decrease** coverage by `0.08%`.
> The diff coverage is `60%`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/356/graphs/tree.svg?width=650&token=0d39OR1fhx&height=150&src=pr)](https://codecov.io/gh/bids-standard/pybids/pull/356?src=pr&el=tree)

```diff
@@            Coverage Diff             @@
##           master     #356      +/-   ##
==========================================
- Coverage   73.27%   73.18%   -0.09%     
==========================================
  Files          24       24              
  Lines        2604     2618      +14     
  Branches      640      642       +2     
==========================================
+ Hits         1908     1916   

--- Comment 15 by yarikoptic ---
But I also I wonder if they minimal sampling rate should be at least twice (or more) of what is computed from that minimal duration to provide some dynamic range for effects of different duration. Otherwise, depending on how rounding done, I guess eg all events of durations from min to 2*min (if flooring/truncating, 1.5 if rounding) would get all just one "bar" and thus wouldn't have any difference between them in there model. 

--- Comment 16 by effigies ---
> But I also I wonder if they minimal sampling rate should be at least twice (or more) of what is computed from that minimal duration to provide some dynamic range for effects of different duration.

I have considered this, and have a few thoughts.

1) We need to consider computational costs vs analytic gains. If the minimum duration is 0.01s, we can resolve it from 0.011s events at a >=10x cost for all operations on the variable. Is the effect on a regressor (and thus potentially a beta map) going to be significant, or are 1ms differences in duration going to be negligible no matter how finely we slice it?
2) Relatedly, the ratio between the minimum and the smallest difference can be very large or small. If we had a minimum of 0.1 and then a lot of durations that are 0.101-0.105, do we want to default to a 0.001 resolution and eat the >100x slowdown? Or is there some maximal ratio to care about?
3) Model writers can specify the sampling rate with `ToDense` transformations, and `

--- Comment 17 by effigies ---
Okay, so do we have anything approaching a consensus? I see a few options percolating, but I think they're fairly closely tied in strategy (tagging with whose proposal they seem closest to, by my reading):

1) Leave it to the user to call `ToDense` as appropriate, possibly using 2 calls in order to capture all events and then downsample to something computatonally manageable. (@tyarkoni)
2) Upsample automatically to capture all events, and compensate for the computational overhead by using a smaller oversampling ratio. (@effigies)
3) Automatically do the 2-step `ToDense` inside `Convolve` (@yarikoptic):
  a. min(shortest duration, smallest difference in durations)
  b. collection sampling rate

Are others that were discussed still in favor with anybody? Of these, I'm feeling 3 would be a pretty good default behavior that can always be overridden by 1.

--- Comment 18 by tyarkoni ---
Re: option 2, I'm not entirely sure that setting oversampling lower will work. At one point in time, that produced buggy results; see nistats/nistats#182. I believe the "fix" for this was to expose the oversampling parameter and set a higher default rather than handling it internally in a principled way (see nistats/nistats#209). If we set it lower to offset the increased sampling rate, I suspect we will just end up with messed-up results again.

--- Comment 19 by effigies ---
I'm happy with 3, if we're all on board.

--- Comment 20 by adelavega ---
@tyarkoni is correct about oversampling. That should never be lower than the shortest event. I think the only option is to downsample. I vote for more explicit. In any case, most users don't have such short events. 

--- END ---