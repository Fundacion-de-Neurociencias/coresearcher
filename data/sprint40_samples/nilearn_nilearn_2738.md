# ENH: compute grey and white matter masks (#2738)
URL: https://github.com/nilearn/nilearn/pull/2738
State: closed | PR: YES
Comments: 77 | Created: 2021-03-20T00:13:55Z | Closed: 2021-06-28T18:21:52Z

## Body (first 1000 chars)
This PR tries to address the issue #2487.


## Comments

--- Comment 1 by alpinho ---
I got 2 errors (1 error duplicated) in my local machine with pytest in lines 632 and 724 of `nilearn/masking.py`, which might be causing many of these failing tests. The problem narrows down to line 223 `nilearn/datasets/struct.py` with the following log:

```
*** nibabel.filebasedimages.ImageFileError: Empty file: '/tmp/pytest-of-analu/pytest-35/temp_nilearn_home4/nilearn_shared_data/icbm152_2009/mni_icbm152_nlin_sym_09a/mni_icbm152_gm_tal_nlin_sym_09a.nii.gz'
```

I don't understand because at the end of the function `check_niimg` in file `nilearn/_utils/niimg_conversions.py`, the `niimg` seems to have been successfully created (it is not empty!), but then there is a problem with the assignment to `gm_img` in line 223 `nilearn/datasets/struct.py`. I have the impression that the issue might come from line 134 of `nilearn/_utils/niimg.py` where dtype is `None`. Any advice? Thx in advance.

--- Comment 2 by NicolasGensollen ---
@alpinho I looked at the errors you're getting with the empty niimg, and I think they come from the fact that you are using datasets fetchers in `compute_brain_mask()`, which are mocked when you run the tests. 

The previous behaviour of `compute_brain_mask()`  was to systematically rely on `load_mni152_brain_mask()` which doesn't download anything, but uses the template `nilearn/nilearn/datasets/data/avg152T1_brain.nii.gz` that is included in nilearn.

--- Comment 3 by alpinho ---
Thanks @NicolasGensollen for the feedback! I am working on your requests. Regarding your last comment about my error, what should I do? Should I just discard this error, since this only happens when running the local tests? Note that the default behavior of `compute_brain_mask()` is still meant to work with the whole-brain mask. I am just adding two more options: the possibility to also compute the gray-matter or 'white-matter' masks.

--- Comment 4 by alpinho ---
@NicolasGensollen I did several updates in order to both fix my previous local pytest errors and address your comments. To fix the local pytest errors, I decided to use the load functions instead of the fetch functions. Therefore, I had to download and store in `nilearn/nilearn/datasets/data/` the gm and wm masks, similarly to what have been done for the whole-brain mask. I didn't abide for the moment with the DRY principles, as suggested by you, since I want to check first whether you agree with this approach. Besides, I am still getting some failing tests. Let me thus know what you think and how I shall proceed.

--- Comment 5 by alpinho ---
> WDYT?

I also prefer to wait for @bthirion comments. I am actually surprised that they don't share already the same resolution... I downloaded these masks from [https://osf.io/7pj92/download](https://osf.io/7pj92/download), i.e. one of the links used by `fetch_icbm152_2009` and, consequently, by `fetch_icbm152_brain_gm_mask`.

--- Comment 6 by alpinho ---
@NicolasGensollen Could you advice what else I should fix?, since I still get many failing tests. I don't get more errors in my local machine with pytest. Thanks in advance!

--- Comment 7 by NicolasGensollen ---
@alpinho I had a look at the test failure that you get. 
First of all, there is only one test failing: `input_data/tests/test_multi_nifti_masker.py::test_compute_multi_gray_matter_mask`. 
In this test, a MultiNiftiMasker is fitted on some random data with a `mask_strategy` set to `template`, which triggers a call to `compute_multi_gray_matter_mask` in `fit()`:

https://github.com/nilearn/nilearn/blob/d066c2375ce2ffd995617551d0c3f4c85836585c/nilearn/input_data/multi_nifti_masker.py#L209-L211

`compute_multi_gray_matter_mask` then calls `compute_brain_mask` with `mask_type` set to `gm`. 
Within this function, the template is loaded and resampled to the provided images before being thresholded. 
I initially thought that the thresholding was zeroing the template out, but it turns out that it is the resampling step which produces an empty template image (all zeros) for `gm` and `wm`. 

Here is a little snippet that reproduces the issue:

```python
import numpy as np
from nilea

--- Comment 8 by NicolasGensollen ---
@alpinho I think the problem happens here (all selected slices are empty...):

https://github.com/nilearn/nilearn/blob/d066c2375ce2ffd995617551d0c3f4c85836585c/nilearn/image/resampling.py#L579-L580

We get to this line because we satisfy this condition:

https://github.com/nilearn/nilearn/blob/d066c2375ce2ffd995617551d0c3f4c85836585c/nilearn/image/resampling.py#L552-L555

I haven't thought too much about it yet, but I think a quick fix would be to force the resampling in `compute_brain_mask`:

```python
resampled_template = cache(resampling.resample_to_img, memory)(template, target_img, force_resample=True)
```

I tried it briefly and it seems to work as expected.

WDYT?

--- Comment 9 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/2738?src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) Report
> Merging [#2738](https://codecov.io/gh/nilearn/nilearn/pull/2738?src=pr&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (373f03a) into [main](https://codecov.io/gh/nilearn/nilearn/commit/78788974cd41aec8698d9c4c4c7a11c47f9baea0?el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (7878897) will **increase** coverage by `0.07%`.
> The diff coverage is `99.05%`.

[![Impacted file tree graph](https://codecov.io/gh/nilearn/nilearn/pull/2738/graphs/tree.svg?width=650&height=150&src=pr&token=KpYArSdyXv&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn)](https://codecov.io/gh/nilearn/nilearn/pull/2738?src=pr&el=tree&utm_medium=referral&utm_source=git

--- Comment 10 by alpinho ---
Thank you very much for your thorough and clear explanation @NicolasGensollen. Your advice also makes sense to me and I have implemented it in my last commit. All checks have passed now. Yet, "Codecov Report" still reports some red segments. Is this problematic?

--- Comment 11 by NicolasGensollen ---
In my opinion, we shouldn't try to tweak the code such that this test pass. I don't think it was really designed to test the behavior of the masker anyway. 
Changing the erosion to 1 results in a non empty mask, but not the one expected by the test.
I would rewrite the test based on the default threshold values that we think are best. 
Does this make sense?

--- Comment 12 by alpinho ---
OK. So, we need to decide now how to change the test function (OR, in alternative, what the default threshold values should be) because  `nilearn/input_data/tests/test_multi_nifti_masker.py::test_compute_multi_gray_matter_mask` is returning zero numpy arrays for `mask` and `mask2`, raising an error in lines 184 and 185. One further note: I reversed the changes I made in the thresholds of some functions in order to avoid confusion.

--- Comment 13 by alpinho ---
Just fixed the whats_new. Can someone else have a look? @bthirion @thomasbazeille @jeromedockes Thx!

--- Comment 14 by jeromedockes ---
> Just fixed the whats_new. Can someone else have a look? @bthirion @thomasbazeille @jeromedockes Thx!

sure!


--- Comment 15 by jeromedockes ---
One concern is that the added images are quite large. adding them makes the source distribution archive of nilearn go from 2.8 M on master to 18 M

it seems they have 1mm resolution and one of them is in float64 ; could we downsample them and store the maskes in int8 and template in float32?
 

--- Comment 16 by bthirion ---
I agree with the dtype change, but I think that there is valuue in having 1-mm resolution images.
While it is goo to reduce the size, I think it is OK to have ~10MB.

--- Comment 17 by jeromedockes ---
ok let's keep 1mm then! casting to smaller types should help, and maybe the files could be gzipped with a higher compression ratio too

--- Comment 18 by alpinho ---
> ok let's keep 1mm then! casting to smaller types should help, and maybe the files could be gzipped with a higher compression ratio too

OK. I changed the dtype to "float32" and compressed the nii files into gzip with the highest compression level, i.e. 9.

--- Comment 19 by jeromedockes ---

> Thx! I am going to start working on this. One question: why should the resolution be a **kwarg instead of a standard arg?

to give it a default value so we don't have to specify it every time,
and so that existing code that doesn't use this parameter continues
working


--- Comment 20 by alpinho ---
I have committed improvements regarding the typecasting, kwarg resolution and downsampling. However, I am uncertain whether my current approach for the downsampling is a good solution. My implementation takes one of the templates available or any other provided by the user with the desired resolution. If the user provides one template at a given resolution, it will resample one of our templates (according whether the user wants whole-brain, gm or wm) for that resolution (lines 653-654). But then, few lines later the template will be again resampled according to the resolution of the target image (650-660). So, I don't think this makes much sense. What I think it should be done is just simply allow for the usage of a different template (at whatever resolution) provided by the user, i.e. lines 653-654 should be removed. Note that for the deprecation cycle, I am using the old template (2mm) through the "resolution" kwarg. Not sure whether "resolution" is the best term here, though. Beside

--- END ---