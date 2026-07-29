# [MRG+1] Region Extractor (#651)
URL: https://github.com/nilearn/nilearn/pull/651
State: closed | PR: YES
Comments: 37 | Created: 2015-07-13T16:08:17Z | Closed: 2015-12-11T08:34:40Z

## Body (first 1000 chars)
Fix #633 
To Do List:
- [x] Code
- [x] Documentation
- [x] Tests
- [x] Example
- Code design
  - `class` named as `RegionExtractor` - to _extract regions_ from the maps and also extracts _subjects timeseries signals_ from those extracted regions by inheriting `NiftiMapsMasker`.
    - function named as `threshold_img` to keep meaningful voxels for region extraction.
    - function named as `connected_regions` to extract regions from thresholded images.
-  `RegionExtractor`
  - `fit()` extract regions.
  - `transform()` regions to signals.
    - example: `plot_extract_regions_canica_maps.py` 
    - example: `plot_extract_regions_smith_atlas_networks.py`
-  `threshold_img` - two different ways of thresholding. (integrated in `nilearn.image.image`)
  1. `percentile` - `scoreatpercentile`.
  2. `img_value` - based on voxel intensity value.
     - example: `plot_extract_regions_statistical_maps.py`
-  `connected_regions` - two different ways of extracting regions.
  1. `local_regions` uses r

## Comments

--- Comment 1 by banilo ---
Why is the new python file camel-cased?


--- Comment 2 by lesteve ---
Rather than saying "imcomplete" just put [WIP] at the beginning of your PR title to indicate this is not ready to merge.


--- Comment 3 by KamalakerDadi ---
Results so far:

``` python
import nibabel

from nilearn import datasets
from nilearn._utils import check_niimg
from nilearn.image import iter_img, new_img_like
from nilearn.decomposition.canica import CanICA

import matplotlib.pyplot as plt
from nilearn import plotting

# ICA Decomposition
adhd_dataset = datasets.fetch_adhd()
func_filenames = adhd_dataset.func

n_components = 5
canica = CanICA(n_components=n_components, smoothing_fwhm=6.,
                memory="nilearn_cache", memory_level=5,
                threshold=3., verbose=10, random_state=0)

canica.fit(func_filenames)
components_img = canica.masker_.inverse_transform(canica.components_)
affine = components_img.get_affine()

# Visualization
for i, img in enumerate(iter_img(components_img)):
    plotting.plot_stat_map(img, title="IC %d" % i,
                           display_mode='z', cut_coords=1,
                           colorbar=False)
    plt.show()

# Foreground Extraction and Connected components extraction
from nilea

--- Comment 4 by KamalakerDadi ---
Remarks:
Random Walker Region Segmentation in progress


--- Comment 5 by KamalakerDadi ---
``` python
import nibabel

from nilearn import datasets
from nilearn._utils import check_niimg
from nilearn.image import iter_img, new_img_like
from nilearn.decomposition.canica import CanICA

import matplotlib.pyplot as plt
from nilearn import plotting

# ICA Decomposition
adhd_dataset = datasets.fetch_adhd()
func_filenames = adhd_dataset.func

n_components = 4
canica = CanICA(n_components=n_components, smoothing_fwhm=6.,
                memory="nilearn_cache", memory_level=5,
                threshold=3., verbose=10, random_state=0)

canica.fit(func_filenames)
components_img = canica.masker_.inverse_transform(canica.components_)
affine = components_img.get_affine()

# Visualization
for i, img in enumerate(iter_img(components_img)):
    plotting.plot_stat_map(img, title="IC %d" % i,
                           colorbar=False)
    plt.show()

from nilearn.region_extraction import SimpleThresholdExtractor
# Foreground extraction using Voxel Ratio or Auto Extractor
vre = SimpleThresholdEx

--- Comment 6 by bthirion ---
Nice, thx ! 
But the naming is a bit twisted. "VoxelRatioExtractor" ? "Threshold of voxel ratio" ?


--- Comment 7 by KamalakerDadi ---
At the moment I kept name as "VoxelRatioExtractor" but need to be discussed to fix a nice and convincing name. "Threshold of voxel ratio", I am trying to say that I applied threshold of `ratio` onto the non zero voxels before "blobs extraction" . The threshold strategy is actually adapted from `canica` script file.


--- Comment 8 by AlexandreAbraham ---
> But the naming is a bit twisted. "VoxelRatioExtractor" ?

This name is a remainder of the piece of code I gave to @KamalakerDadi. I take your remark as a compliment about my natural gift to find perfect names for objects (remember the NiftiBallsMasker?).


--- Comment 9 by AlexandreAbraham ---
How are things going? Don't hesitate to push!


--- Comment 10 by KamalakerDadi ---
Random Walker is in progress. I will push once its done.


--- Comment 11 by KamalakerDadi ---
I have pushed most recent changes and documented with more meaning to each parameter. Constrains I have is designing `voxel ratio` or `seed ratio`. Till this changes method works fine with leaving to `default` options. 

Tomorrow, I need to discuss a way to design thresholding when a user chooses to input `ratio` a float value. @GaelVaroquaux @AlexandreAbraham 

To make design more robust. Comments till now are welcome.


--- Comment 12 by KamalakerDadi ---
As discussed with @GaelVaroquaux @AlexandreAbraham  , a new design is to be done which is to include, `NiftiMapsMasker` as a `subclass` in the design and try to extract signals at a time by breaking the components apart.
So, it is like this:
1. Break the components apart
2. Extract signals using `NiftiMapsMasker` using `fit_transform`.

I feel for me it will take some time to push new inclusions.
I am working on designing a `auto threshold` strategy.

But, if want me push recent changes. I will do that. I have addressed all recent comments except,
comment 1

> Well, problems are meant to be solved ;). I gave you several options to solve them.
>    Your solution here is a workaround to aboid the fact that you need the brain mask: you suppose that  nonzero values are the only one not masked, which is wrong.

comment 2

>  I think that we can be more restrictive using check_niimg_4d.
>  @GaelVaroquaux : people will want to extract regions from simple 3d images too
>  but, in that case, th

--- Comment 13 by AlexandreAbraham ---
> But, if want me push recent changes. I will do that.

Pushing is generally a good practice. Basically, the "[WIP]" tag in your PR title means that you are working on it and that, if you need comments, you will ask for them explicitely. We generally don't review PR that are "WIP". So it is safe for you to push ;).


--- Comment 14 by KamalakerDadi ---
With this implementation, there is a slight trade-off with size of the `n_components` and `scoreatpercentile` and `min_size`.

If `n_components = 10` are more, then obviously `percentile` is higher since it depends on the length of the maps and `min_size`. It works perfectly.

If `n_components = 4` are less, then  `percentile` is low and we need to slightly decrease `min_size` to get regions/blobs seperated.

Also @AlexandreAbraham , I don't know whether to remove `scoreatpercentile` or keep it. I suppose we had discussion on making `canica` compatibility.


--- Comment 15 by KamalakerDadi ---
This commit has nothing to do with discussed new design. It is just an old one with some changes according to comments.


--- Comment 16 by AlexandreAbraham ---
My thoughts on your previous post: I have the impression that you are trying to address the specific problem of CanICA maps that you showed me. You _should not_ try to tweak your algorithm for that particular case. You have the description of an algorithm, you just have to implement it. To test your algorithm, you can generate toy data (which is a good practice since it can be reused for examples afterward) or, your case, clean data such as the smith atlas.

Once the algorithm is implemented, then we can see if it works in real life and do the appropriate adptations. For example, I think that another criterion, like `max_regions_per_map` is very useful in practice, but we will see that later.

As I told you "garbage in, garbage out". If the user feeds crappy noisy maps with lots of regions and do not tweak the parameters accordingly, the problem is not on your side.


--- Comment 17 by KamalakerDadi ---
@AlexandreAbraham  I have added code snippet of yours to compute `threshold` using `ratio` of the number of voxels. Please see if it makes sense as how I included. Also, I kept `scoreatpercentile` as an option.


--- Comment 18 by AlexandreAbraham ---
@KamalakerDadi, I have no time to test your code but the logic looks good to me. I switch into code nazi mode and nitpick on implementation details.


--- Comment 19 by KamalakerDadi ---
@AlexandreAbraham Could you have a look into this ?
I have changed the design flaw. RegionExtractor `fit` will extract the regions and `fit_transform` will extract the timeseries signals from extracted regions. `NiftiMapsMasker` is used in most cases.


--- Comment 20 by KamalakerDadi ---
@GaelVaroquaux @AlexandreAbraham @lesteve I think it can be reviewable. For coverage increase, I have tried to include tests from skimage for the missing lines. But, still I see there are some missing lines. I will see it. Any comments on code, ported files and locations will be helpful. Thanks.


--- END ---