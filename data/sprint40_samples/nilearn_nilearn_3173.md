# Allow not scaling background maps for surface plots (#3173)
URL: https://github.com/nilearn/nilearn/pull/3173
State: closed | PR: YES
Comments: 59 | Created: 2022-03-07T17:24:32Z | Closed: 2023-03-08T17:18:41Z

## Body (first 1000 chars)
Closes #3169 .

Currently, this PR:
- enables `bg_on_data` for `plotly` engine
- implements `scale_bg_map` for `matplotlib` and `plotly` engines

I still have to:
- [x] enable `bg_on_data` and `scale_bg_map` for `view_surf()`
- [x] add an example (and / or edit existing ones) using this feature

## Comments

--- Comment 1 by github-actions[bot] ---
👋 @alexisthual Thanks for creating a PR!

Until this PR is ready for review, you can include the [WIP] tag in its title, or leave it as a github draft.

Please make sure it is compliant with our [contributing guidelines](https://nilearn.github.io/development.html#contribution-guidelines). In particular, be sure it checks the boxes listed below.
- [ ] PR has an interpretable title.
- [ ] PR links to Github issue with mention "Closes #XXXX"
- [ ] Code is PEP8-compliant.
- [ ] (Bug fixes) There is at least one test that would fail under the original bug conditions.
- [ ] (New features) There is at least one unit test per new function / class.
- [ ] (New features) The new feature is demoed in at least one relevant example.

We will review it as quick as possible, feel free to ping us with questions if needed.

--- Comment 2 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/3173?src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) Report
> Merging [#3173](https://codecov.io/gh/nilearn/nilearn/pull/3173?src=pr&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (a40ee06) into [main](https://codecov.io/gh/nilearn/nilearn/commit/f6db5d424cfb794dd9cf4ea93d8319e5fbc4565b?el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=nilearn) (f6db5d4) will **increase** coverage by `0.09%`.
> The diff coverage is `100.00%`.

> :exclamation: Current head a40ee06 differs from pull request most recent head 7157971. Consider uploading reports for the commit 7157971 to get more accurate results

```diff
@@            Coverage Diff             @@
##             main    #3173      +/-   ##
==========================================
+ Coverage   90.93%   91.02%  

--- Comment 3 by alexisthual ---
Here are a few snippets working with the current implementation:

Base snippet to run before the others:
```python
import matplotlib.pyplot as plt
from nilearn import datasets, plotting, surface
import numpy as np

from importlib import reload

# %% Load fsaverage5
fs5 = datasets.fetch_surf_fsaverage()
fs7 = datasets.fetch_surf_fsaverage(mesh="fsaverage7")

# %% Load sulc surface from fsaverage
sulc_fs5 = surface.load_surf_data(fs5.sulc_left)
sulc_fs7 = surface.load_surf_data(fs7.sulc_left)
# Create binary map indicating sulci and gyri
sulc_sign_fs5 = (np.sign(sulc_fs5) + 1) / 8 + 0.25
sulc_sign_fs7 = (np.sign(sulc_fs7) + 1) / 8 + 0.25
sulc_norm_fs5 = sulc_fs5 - sulc_fs5.min()
sulc_norm_fs5 = sulc_fs5 / sulc_fs5.max()
sulc_norm_fs7 = sulc_fs7 - sulc_fs7.min()
sulc_norm_fs7 = sulc_fs7 / sulc_fs7.max()

# %% Load random contrast map
motor_images = datasets.fetch_neurovault_motor_task()
surf_fs5 = surface.vol_to_surf(motor_images.images[0], fs5.pial_left)
surf_

--- Comment 4 by jeromedockes ---
Thanks a lot @alexisthual  I can't do a full review this week but I think the new plots are really cool. Actually I think we should make it easy to use the binary backgrounds that you show (`sulc_sign*`), either by defining sentinel values for bg_map or by adding a keyword like `binarize_bg`. we may even want to make it the default.
+1 for adding it to view_surf because we want to keep the interfaces consistent as much as possible

--- Comment 5 by alexisthual ---
> Thanks a lot @alexisthual  I can't do a full review this week but I think the new plots are really cool. 
Actually I think we should make it easy to use the binary backgrounds that you show (`sulc_sign*`), either by defining sentinel values for bg_map or by adding a keyword like `binarize_bg`. we may even want to make it the default.

No worries, this doesn't have to be merged soon.
Moreover, you are right, I think it's important we get the API as simple as possible here.

`scale_bg_map` clearly is not be the best name. Besides, maybe it would make sense to have a dedicated `sulc_map` attribute to implement what you suggest, and a `sulc_map_mode` (name is terrible but please bear with me) instead of `scale_bg_map` which could be "linear", "sign", "both", "custom" to generate all previous rendering effects.

Overall, it feels to me that `bg_map` was originally introduced to cope with flat lightning issues coming from `matplotlib`, but we could find a different way to deal with this pr

--- Comment 6 by alexisthual ---
Here is a new plot which make me think that it makes more sense to keep `bg_map` and not add `sulc_map`, contrary to what I had previously suggested.

Indeed, after experimenting a bit, I think people use the curvature sign (and not the sulc sign), which yields a much nicer rendering:

```python
plotting.plot_surf(
    fs7.infl_left,
    surf_fs7,
    cmap="coolwarm",
    threshold=1.5,
    bg_map=curv_sign_fs7 + sulc_norm_fs7 / 8,
    bg_on_data=True,
    scale_bg_map=False,
)
plt.show()
```

![Screenshot from 2022-03-08 17-05-26](https://user-images.githubusercontent.com/13835654/157277950-fc3a3613-ebde-437c-bc28-7e04c1cd0c8d.png)

On a different note, it also works well for flat maps (see #3171 for more info):

```python
flat_fs7 = "/home/alexis/singbrain/fsaverage_flat/surfaces/flat_lh.gii"

# %%
fig = plotting.plot_surf(
    flat_fs7,
    surf_fs7,
    cmap="coolwarm",
    threshold=1.5,
    bg_map=curv_sign_fs7,
    bg_on_data=True,
    scale_bg_ma

--- Comment 7 by alexisthual ---
In the last commits, I tried to make sure that all surface plotting methods (including `view_surf` and `view_img_on_surf`) have `bg_on_data`, `scale_bg_map` and `darkness`.

I also edited what I reckon is the [main nilearn example for plotting surfaces](https://nilearn.github.io/stable/auto_examples/01_plotting/plot_3d_map_to_surface_projection.html#sphx-glr-auto-examples-01-plotting-plot-3d-map-to-surface-projection-py), so that it shows how to use `scale_bg_map=False`. I modified the first generated image on purpose, so that it will eventually modify the thumbnail of this example, in order for this feature to be easier to find.
Maybe we could use `fsaverage7` in the first image so that it looks nicer. For now, it looks like this on `fsaverage5` (with matplotlib and plotly respectively):

![Screenshot from 2022-09-27 19-07-06](https://user-images.githubusercontent.com/13835654/192593670-d70dec4e-ba80-4f44-865c-caef85700b67.png)
![Screenshot from 2022-09-27 19-07-20](https://user

--- Comment 8 by jeromedockes ---
> Maybe we could use `fsaverage7` in the first image so that it looks nicer. For now, it looks like this on `fsaverage5` (with matplotlib and plotly respectively):

that's true but the reason for using the small mesh is to build the documentation faster. Also plotly plots with large meshes consume a lot of memory and we don't want the documentation pages to be too heavy

--- Comment 9 by jeromedockes ---
> Otherwise, I noticed that the 'darkness' parameter is reminicent of the 'dim' parameter in plot_img functions. We should probably reunify the API here, but go first through deprecation cycles.

I agree. Neither of these is great; "dim" sounds like "dimension"; "darkness" has a surprising behavior: increasing the darkness makes the image lighter; neither name hints that it is a scaling factor

--- Comment 10 by alexisthual ---
> I agree. Neither of these is great; "dim" sounds like "dimension"; "darkness" has a surprising behavior: increasing the darkness makes the image lighter; neither name hints that it is a scaling factor

Maybe `bg_brightness` / `bg_lighting` would be more intuitive?

--- Comment 11 by alexisthual ---
> I agree. Neither of these is great; "dim" sounds like "dimension"; "darkness" has a surprising behavior: increasing the darkness makes the image lighter; neither name hints that it is a scaling factor

Actually, I did a few more tests: `darkness=0` gives a perfectly white background, while `darkness=1` allows to display dark shades, so maybe renaming it to `bg_brightness` doesn't make sense (however, `bg_darkness` would probably be more intuitive?).

Here are some more thoughts about this PR:
- @jeromedockes rightly pointed out that my current color mixin method is rather poorly designed, and that using a [correct mixin function](https://stackoverflow.com/a/727339/7445658) would make more sense
  - using such a mixin function, we could replace `bg_on_data` with a parameter `alpha` to set the surface image transparency, which I think would make a lot of sense (`bg_on_data=True` could default to setting `alpha=0.5` until we deprecate `bg_on_data`)
  - when calling `plot_surf()`,

--- Comment 12 by bthirion ---
Ths does not look bad. One of my worries is that apparently different kw are use for a similar (?) meaning/effect: `dim` in plottting function vs `bg_darkness` for surfaces. We should ideally reunify the logic in the API. Otherwise, I find your proposition quite clean.


--- Comment 13 by alexisthual ---
Ok so maybe we could plan to do it this way:
- (in this PR) rename `scale_bg_map` to `bg_scale_map`
- (in another PR) rename `darkness` and `dim` to `bg_darkness` with deprecation cycle
- (in another PR) rename `alpha` to `bg_alpha`, deprecate `bg_on_data` and handle `alpha` to tweak surface map transparency

Also, just as a comment not to forget it:
- (in another PR) rename `one_mesh_info()` and `full_brain_info()`  (so that they don't seem like public methods)

Besides, I think allowing to set `alpha` values for surface maps could help pave the way towards being able to plot several surface maps at the same time (cf #3189, and many more people have verbally asked me how to do this).

--- Comment 14 by jeromedockes ---
I understand the motivation for allowing to choose a different background in `view_img_on_surf` but it should be replaced with a sensible default. ATM the default is sulcal depth of fsaverage mesh and it is replaced with no background.
```python
from nilearn import datasets, plotting

img = datasets.fetch_neurovault_motor_task()["images"][0]
display = plotting.view_img_on_surf(img, threshold=2)
```

yields on main branch 

![screenshot_2022-10-24T15:18:25-04:00](https://user-images.githubusercontent.com/9196501/197608169-7a97d0e9-e86d-4e04-93a6-cdf59b7b49e3.png)

and with latest commit in this PR (f8002bb)

![screenshot_2022-10-24T15:18:10-04:00](https://user-images.githubusercontent.com/9196501/197608271-433aee37-39a6-4069-875f-8ae695ae7ab5.png)


--- Comment 15 by jeromedockes ---
> Actually, I did a few more tests: `darkness=0` gives a perfectly white background, while `darkness=1` allows to display dark shades, so maybe renaming it to `bg_brightness` doesn't make sense (however, `bg_darkness` would probably be more intuitive?).

Ah yes, because we use the 
[Greys](https://matplotlib.org/stable/tutorials/colors/colormaps.html#sequential)
colormap, for which lower values are lighter and higher values are darker.
- darkness = 0 → set all background to white
- darkness in (0, 1) → make background lighter
- darkness = 1 → don't change the background
- darkness > 1 → make background darker

that seems reasonable but do we have any help for users re. what value to pick for a darker background? or maybe it could be reparametrized so that
- darkness = -1 → white
- darkness in (-1, 0) → brighter
- darkness = 0 → original
- darkness in (0, 1) → darker
- darkness = 1 → black

(or the opposite with "brightness")



--- Comment 16 by jeromedockes ---
> (in this PR) rename `scale_bg_map` to `bg_scale_map`

I don't love `bg_scale_map` -- I think it's harder to guess what it does than `scale_bg_data`. but I do see the value of having all background-related stuff start with `bg` . I am also a bit worried about the proliferation of parameters. Do you think we could do without the bg scaling parameter? In that case, the default bg maps we would use would be scaled ones (if we still want scaling by default), and if a user wants scaling for a user-provided map they could scale it themselves?

--- Comment 17 by jeromedockes ---
> Besides, I think allowing to set `alpha` values for surface maps could help pave the way towards being able to plot several surface maps at the same time (cf #3189, and many more people have verbally asked me how to do this).

I like the idea of specifying an `alpha` for the foreground map and doing transparency explicitly. it is easier to understand than `bg_on_data` and as you say it will be easier to extend. for example we could imagine providing an alpha map rather than a hard threshold. thanks for looking up how to mix colors correctly

still about reducing the number of parameters, do we really need the background alpha -- ie do we often want to see the mesh wireframe and see through the brain? my guess would be that with the appropriate background map we don't need it and it doesn't look good and makes it hard to visualize the map

--- Comment 18 by alexisthual ---
I agree that setting transparency for background maps probably isn't useful and that we could deprecate this parameter.
Moreover, maybe we could remove `darkness` (ie `bg_darkness`) altogether and assume that users who want to have lighter/darker background maps could scale them themselves and use `bg_scale_map=False`.

Doing so, 3 parameters would disappear (`bg_on_data`, `alpha` (ie `bg_alpha`) and `darkness`), and 2 would be created (`bg_scale_map` and `alpha`), while giving more power to users.

I agree that `bg_scale_map` may seem less explicit than `scale_bg_map`. I would lean towards using `bg_scale_map` but I don't have strong feelings on this.

> I understand the motivation for allowing to choose a different background in `view_img_on_surf` but it should be replaced with a sensible default. ATM the default is sulcal depth of fsaverage mesh and it is replaced with no background.
> 
> ```python
> from nilearn import datasets, plotting
> 
> img = datasets.fetch_neurov

--- Comment 19 by jeromedockes ---
> I agree that setting transparency for background maps probably isn't useful and that we could deprecate this parameter.
> Moreover, maybe we could remove `darkness` (ie `bg_darkness`) altogether and assume that users who want to have lighter/darker background maps could scale them themselves and use `bg_scale_map=False`.

I think so, as long as we make sure plots look good with possible
default choices such as fsaverage sulcal depth or curvature sign.

>
> Doing so, 3 parameters would disappear (`bg_on_data`, `alpha` (ie `bg_alpha`) and `darkness`), and 2 would be created (`bg_scale_map` and `alpha`), while giving more power to users.
>

That's good! The only thing I find a bit problematic is the alpha formal
parameter is kept but its meaning changes -- maybe it could be fg_alpha
or something like that.

> I agree that `bg_scale_map` may seem less explicit than `scale_bg_map`. I would lean towards using `bg_scale_map` but I don't have strong feelings on this.

me neither. Maybe bg_ma

--- Comment 20 by alexisthual ---
> I think so, as long as we make sure plots look good with possible default choices such as fsaverage sulcal depth or curvature sign.

Yes I agree, I should probably come up with a scaling strategy and a default value for `darkness` (which would become a backstage variable) so that both maps you refer to look nice. It sounds doable!

> in the plot_surf etc. the user provides a surface and bg map explicitly, but in view_img_on_surf they provide a volume image. plot_img_on_surf also uses fsaverage sulcal depth by default. I'm completely fine with using something else than sulcal depth, but replacing it with an empty map results in worse plots with the default arguments, so it's not a very good change for users.

Oh I see! It all makes a lot more sense to me now. If that's ok with you, I'll make the "curv sign" background map the default then, as I think it shows more information :slightly_smiling_face: 

> Maybe bg_map_rescale, bg_map_rescaling or something like that.

Yaaay, I

--- END ---