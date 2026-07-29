# [MRG+1] Adding a 4Dplot function displaying as a contours in img_plotting  (#589)
URL: https://github.com/nilearn/nilearn/pull/589
State: closed | PR: YES
Comments: 40 | Created: 2015-05-16T18:02:05Z | Closed: 2015-07-16T13:35:26Z

## Body (first 1000 chars)
Edited by @AlexandreAbraham
- [x] thicken contour lines
- [x] add an example of plotting with several atlases
- [x] make code PEP8 compliant
- [x] for thresholding, accept one value, or a list of values, or a percentage, or a list of percentage

I have basically utilised the content of the code and documentation of each arguments for writing a function called `plot_4d` in `img_plotting`.
Here is the code snippet to call the function `plot_4d` for plotting in contours. 
Harvard Oxford Atlas:

``` python
from nilearn import datasets, plotting
import matplotlib.pyplot as plt
atlas_img_4D, labels = datasets.fetch_harvard_oxford('cort-prob-2mm')
display = plotting.img_plotting.plot_4d(atlas_img_4D)
plt.show()
```

Result:
![figure_1](https://cloud.githubusercontent.com/assets/11410385/7667394/2952f1ae-fc06-11e4-8055-70f6ba96a2b2.png)

MSDL Atlas:

``` python
from nilearn import datasets, plotting
import matplotlib.pyplot as plt
atlas_data = datasets.fetch_msdl_atlas()
atlas_filename = atlas

## Comments

--- Comment 1 by KamalakerDadi ---
issue #588 


--- Comment 2 by AlexandreAbraham ---
I am wondering if we want to have such a function instead of educating the user about how to display several regions himself. The only additional logic in this function is the way the colormap is computed, which is a pain in matplotlib but for which we can provide a utility function.

I have one myself and so to do the same thing I write:

``` python
p = plot_anat(...)

for region_img, color in zip(iter_img(atlas_img), get_colors('gist_rainbow', len(atlas_img.shape[-1]))):
    p.add_countours(region_img, ...)
```

What would be (in my sense) a good addition for such function:
- a "group" heuristic for `find_cut_coords` because it will always be centered here I think (but this may be something to add in the slicer itself, an update of the cut coords when contours or overlays are added)
- an intelligent coloring code. Here, neighboring regions have similar colors because the atlas is made this way. We should write an algorithm to have maximum contrast between neigboring regions, this is 

--- Comment 3 by GaelVaroquaux ---
> I am wondering if we want to have such a function instead of educating
> the user about how to display several regions himself.

This will provide a lot of value for beginners. It's a feature that many
people have been curious about. Also, many of us have a copy-pasted
variant of this code. Getting is right is somewhat challenging, and each
time someone rewrites it, its time lost.

When something keeps coming up in people's code, it's often a good thing
to make a function out of it. Also, we are going to need it to make the
output of the ICA.


--- Comment 4 by AlexandreAbraham ---
Well, in that case, I would say that we need to support maps and labels. Maybe an `iter_map` function would be useful. It would iterate on 4d if there is one, and if it is 3D with integer values (ie labels), it would return a binary mask corresponding to each label.


--- Comment 5 by GaelVaroquaux ---
I would provide 2 functions, and not do magic, but have a good error
message. We already have the first function: plot_roi.


--- Comment 6 by KamalakerDadi ---
I am thinking more or less like a enhancement to plotting functions, for example 4D. As far as I have seen, there is no specific example describing plotting 4D. As a users point, I thought it would be nice to input data and view the maps as an overlay or contours on the anatomical image.


--- Comment 7 by KamalakerDadi ---
Examples with Harvard Oxford, MSDL atlases: default `threshold` mode

``` python
from nilearn import datasets, plotting
# Harvard Oxford Atlas
atlas_img_4D = datasets.fetch_harvard_oxford('cort-prob-2mm')
# Visualization of Harvard Oxford Atlas maps as a contours type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0], 
                                                title='Harvard-Oxford with contours')
# Visualization of Harvard Oxford Atlas maps as a continuous type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0], view_type='continuous',
                                                title='Harvard-Oxford with continuous')
```

Output:
![hocontours](https://cloud.githubusercontent.com/assets/11410385/7909869/ee77dd96-084f-11e5-8ac0-145d487b6aa7.png)

![hocontinuous](https://cloud.githubusercontent.com/assets/11410385/7909871/f46734d6-084f-11e5-8ea6-37cfade51177.png)

MSDL Atlas Example:

``` python
from nilearn import datasets, plotting
# MSDL Atlas
atl

--- Comment 8 by AlexandreAbraham ---
> As I see I missed the "label = 0", which is "Frontal Pole"

I don't see how you can lose a region with this threshold strategy. Could you add some debug info, like the min and max of the frontal pole map and the computed threshold?


--- Comment 9 by AlexandreAbraham ---
> To avoid maximum overlaps between each maps, I used less value `threshold=1e-1`.

For me, this value has no sense. What we said about threshold:
- if threshold is a string, it must look like "38%" and, in that case, we keep all the values that are, in absolute, above the threshold of 38%
- if threshold if a float, we use this value as a threshold
- if threshold is a list, then the same rules as above apply but each map has a different threshold

You can take a look at the parameter `edge_threshold` of `plot_connectome` which is handled the same way.


--- Comment 10 by KamalakerDadi ---
After addressing some comments: 
**Fixing contour fillings using contourf**
Output: 

``` python
import matplotlib.pyplot as plt
from nilearn import datasets, plotting

# Harvard Oxford Atlas
atlas_img_4D = datasets.fetch_harvard_oxford('cort-prob-2mm')
# Visualization of Harvard Oxford Atlas maps as a contours type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0],
                                                title='Harvard-Oxford with contours')
# Visualization of Harvard Oxford Atlas maps as a contour fillings type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0], fill=True,
                                                title='Harvard-Oxford with contour fillings')
# Visualization of Harvard Oxford Atlas maps as a continuous type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0], view_type='continuous',
                                                title='Harvard-Oxford with continuous')
plt.show()
```

**contours**
**continuous over

--- Comment 11 by AlexandreAbraham ---
@GaelVaroquaux I'm not convinced by the filled contours and I think that we should let the user decide if he wants them or not. Do you agree with that? If so, should we add a `view_type` or a kwarg?


--- Comment 12 by GaelVaroquaux ---
I agree that we should let the option open. It can be useful, as can be seen on figures from Yannick's paper.

Sent from my phone. Please forgive brevity and mis spelling

On Jun 9, 2015, 07:02, at 07:02, Alexandre Abraham notifications@github.com wrote:

> @GaelVaroquaux I'm not convinced by the filled contours and I think
> that we should let the user decide if he wants them or not. Do you
> agree with that? If so, should we add a `view_type` or a kwarg?
> 
> ---
> 
> Reply to this email directly or view it on GitHub:
> https://github.com/nilearn/nilearn/pull/589#issuecomment-110365075


--- Comment 13 by AlexandreAbraham ---
You still have cosmetics details to solve. Apart from that, the code is ready.


--- Comment 14 by KamalakerDadi ---
@GaelVaroquaux We addressed most of the comments and I will push the code with these changes with some tests.


--- Comment 15 by KamalakerDadi ---
Example which displays Harvard-Oxford, MSDL and Smith 2009 atlas maps:
- Harvard Oxford

``` python
import matplotlib.pyplot as plt
from nilearn import datasets, plotting

# Harvard Oxford Atlas
atlas_img_4D = datasets.fetch_harvard_oxford('cort-prob-2mm')
# Visualization of Harvard Oxford Atlas maps as a contours type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0],
                                                title='Harvard-Oxford with contours')
# Visualization of Harvard Oxford Atlas maps as a contour fillings type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0], filled=True,
                                                title='Harvard-Oxford with contour fillings')
# Visualization of Harvard Oxford Atlas maps as a continuous type
display = plotting.img_plotting.plot_prob_atlas(atlas_img_4D[0], view_type='continuous',
                                                title='Harvard-Oxford with continuous')
plt.show()
```
- MSDL

``` python
import 

--- Comment 16 by KamalakerDadi ---
@GaelVaroquaux Pushed some changes. Balance as of now is to add smoke tests.


--- Comment 17 by bthirion ---
Looks great. Are you providing an example with these displays ?


--- Comment 18 by KamalakerDadi ---
Yes definitely. I have no specific thing to work on. May be an example should be using canica maps ?


--- Comment 19 by bthirion ---
Or just the same as you did with atlases ? The advantage is that the example would be faster (no computation involved), which is better if the purpose is to illustrate the visualization capabilities of Nilearn.


--- Comment 20 by GaelVaroquaux ---
@KamalakerDadi : this is looking good. Now you need to work on the documentation (you need to add an entry to the plotting.rst documentation page) and the examples. It's important to get good wording.


--- END ---