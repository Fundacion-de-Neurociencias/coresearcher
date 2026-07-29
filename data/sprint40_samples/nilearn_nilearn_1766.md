# switch from papaya to brainsprite in plotting.view_stat_map (#1766)
URL: https://github.com/nilearn/nilearn/pull/1766
State: closed | PR: YES
Comments: 166 | Created: 2018-09-28T04:53:45Z | Closed: 2018-11-10T07:22:56Z

## Body (first 1000 chars)
I really love the new 3D interactive viewer (`plotting.view_stat_map`), but the notebooks it is producing are huge. In this PR, I am proposing to switch from papaya to brainsprite, which is a js library I developed for the exact purpose of embedding lightweight 3D viewers in html pages (http://github.com/simexp/brainsprite.js).

The first difference with papaya is that it is using a jpg or a png containing all sagital slices of a volume as well as json metadata to store the brain images. That tend to be quite smaller than a nifti (depending on the numerical precision of the nifti). That also means that brainsprite can render brains with core html5 features, and no dependencies. So the brainsprite library weighs 15kb (500 lines...), as opposed to 2Mb for the current papaya html template. I have attached two brain viewers embedded in jupyter notebooks. The [Papaya-based notebook](http://nbviewer.jupyter.org/github/pbellec/misc/blob/master/example_view_stat_map_papaya.ipynb) is 12Mb, wh

## Comments (first 1000 chars each)

--- Comment 1 by cdansereau ---
That would be a great feature to add.

--- Comment 2 by GaelVaroquaux ---
I just tested the functionality, and it works very well. In addition to
the memory savings (which are a big deal), I also prefer the
look-and-feel. The fact that it is very similar to what the other
plotting functions give is very useful. In particular the display of the
cut coordinates. Thank you!

A few comments on the look and feel:

- Could we have the same default behavior as plot_stats_map: threshold
  being set to 1e-6, to cut out near zeros.

- The IFrame is now too tall. Can you make it smaller, so that it fits
  closely the plot. This more compact view will be, by itself, a good
  gain. Indeed, I found that working in a complex jupyter notebook with
  those very large plots was not very convenient.

Maybe more later. I need to switch to something else.


--- Comment 3 by lunebellec ---
@GaelVaroquaux great to hear you like it!

I ran the code through http://pep8online.com/ and fixed all detected issues. 
  It's updated now. 

For the iframe, I will make it fit (and try to adjust size to screen, currently even the papaya viewer is broken when visualized on a phone). 

For the threshold, I tried but somehow the result is inconsistent  with plot_stat_map. I'll dig further. 

As I said there are lots of work left, from the tests to the doc, to other minor things listed [here](https://github.com/brainsprite/brainsprite.py/issues).
  Will resolve everything asap.

--- Comment 4 by jeromedockes ---
this will be a great improvement. thanks a lot! I'll add some more detailed comments later this week

--- Comment 5 by lunebellec ---
I think I solved the fit of the iframe. Check this [example](http://nbviewer.jupyter.org/github/pbellec/misc/blob/master/example_view_stat_map_brainsprite.ipynb) to see how it looks now.

To solve this issue, I had to change the code of `js_plotting_utils.py` a bit. Before the size of the iframe was set to 600 x 400 (in pixels), by the `width` and `height` properties. That did not work with brainsprite (aspect ratio is more 10:5 than 3:2), and also did not scale to, say, a phone.

With the new code, `width` is expressed as a percentage of the parent element on the page (typical range 0-100, although one may want to work with width >100).

`height` has disappeared, and is replaced by `ratio`, which is height/width, in percentage (again, possible to go beyond 100% to get portrait orientation). 
 
I've set the default width at 75%, and the default ratio at 68%. I've checked and [`view_connectome`](http://nbviewer.jupyter.org/github/pbellec/misc/blob/master/example_view_connectome.

--- Comment 6 by jeromedockes ---
>  I was able to simply use a bootstrap class to get the desired behaviour, and the code is quite concise. I could also implement a pure css `style`, the code would just be longer

I think I would prefer to write the style rather than use a bootstrap class, in case someone wants to put the brainsprite in a webpage that doesn't use bootstrap

--- Comment 7 by jeromedockes ---
why did the jquery version need to change?

--- Comment 8 by jeromedockes ---
please run flake8 again, there are a few things to fix, in particular unused imports and variables

--- Comment 9 by jeromedockes ---
![screenshot from 2018-10-07 19-48-35](https://user-images.githubusercontent.com/9196501/46584931-1e63c800-ca6a-11e8-9d1a-d7ac73a52ef6.png)

I sometimes see some weird gray pixels, what are they due to?

to reproduce:

    >>> data = datasets.fetch_localizer_button_task(get_anats=True)
    >>> img = data['tmaps'][0]
    >>> anat = data['anats'][0]
    >>> v = plotting.view_stat_map(img, threshold=2., bg_img=anat)



--- Comment 10 by jeromedockes ---
![screenshot from 2018-10-07 20-01-20](https://user-images.githubusercontent.com/9196501/46585050-e067a380-ca6b-11e8-8280-5fa44228886b.png)

actually, i also see some such pixels in papaya viewer with master, but they are harder to see. they don't appear in matplotlib plots

--- Comment 11 by lunebellec ---
> ![screenshot from 2018-10-07 19-48-35](https://user-images.githubusercontent.com/9196501/46584931-1e63c800-ca6a-11e8-9d1a-d7ac73a52ef6.png)
> 
> I sometimes see some weird gray pixels, what are they due to?
> 
> to reproduce:
> 
> ```
> >>> data = datasets.fetch_localizer_button_task(get_anats=True)
> >>> img = data['tmaps'][0]
> >>> anat = data['anats'][0]
> >>> v = plotting.view_stat_map(img, threshold=2., bg_img=anat)
> ```

Actually I believe this is the same issue I noticed when I tried to implement the default threshold at 1e-6. The result is super weird (see image attached comparing `view_stat_map` and `plot_stat_map`. 

This may have to do with the fact that the functional volume is resampled from native space to the background space (using isotropic voxels) *before* the threshold is applied. This may introduced some interpolation artefacts. But you are saying that it does not show up in matplotlib, so that suggests it's not the problem.

Another option is th

--- Comment 12 by kchawla-pi ---
Hi @pbellec Thanks for doing this!
I noticed that many of the function in the .py files are super long. Consider refactoring them into multiple smaller functions, a ballpark of 7-8 commands per sub-function. 
This will simplify debugging, and future maintenance and improvements considerably.
We are starting a push to refactor the code and if new contributions adhere to the practice it will be a huge help.

--- Comment 13 by lunebellec ---
> > I was able to simply use a bootstrap class to get the desired behaviour, and the code is quite concise. I could also implement a pure css `style`, the code would just be longer
> 
> I think I would prefer to write the style rather than use a bootstrap class, in case someone wants to put the brainsprite in a webpage that doesn't use bootstrap

I am having second thoughts about the strategy to resize the iframe.
  I think I am going to revert to a fixed width / height for now, and simply adapt these numbers for brainsprite.
    
In any case we will need different rules for different screen sizes, so let's discuss this in another thread.
  I will make a separate PR for scaling iframes once brainsprite is merged. 

All I will do in the `js_utils` is to remove the border of the iframe.


--- Comment 14 by lunebellec ---
> Hi @pbellec Thanks for doing this!
> I noticed that many of the function in the .py files are super long. Consider refactoring them into multiple smaller functions, a ballpark of 7-8 commands per sub-function.
> This will simplify debugging, and future maintenance and improvements considerably.
> We are starting a push to refactor the code and if new contributions adhere to the practice it will be a huge help.

Yes, I agree. There are several parts of the code that could be naturally splitted. Will work on this. 

--- Comment 15 by lunebellec ---
> why did the jquery version need to change?

It doesn't, but brainsprite somehow broke with the newer version. I reverted back to an old version to open the PR, but I will update and fix the incompatibility asap.

--- Comment 16 by GaelVaroquaux ---
> I don't think that particular snippet exists as an independent function.
> It is taken from nilearn/plotting/displays.py#L754-L772
> The right move would be to create a small private function in displays.py, and
> then simply re-use in html_stat_map.
> I was planning to deal with this in a separate PR.

Feel free either to do a separate PR that we merge before, or to do it in
this PR.


--- Comment 17 by jeromedockes ---
> I think I am going to revert to a fixed width / height for now, and simply adapt these numbers for brainsprite

I think that's a good idea, making the displays responsive and replacing papaya with brainsprite are independent improvements

--- Comment 18 by lunebellec ---
> I sometimes see some weird gray pixels, what are they due to?

So the reason for these gray pixels was that I generated the image using the "greyed out" colormap. 
Because of interpolation and binning of values, some values that survive the threshold actually fall within the grey zone of the colormap.
This was easy to fix: as I separately generate the sprite and the colormap, I simply used a non-greyed colormap for the sprite.
Also, the weird pattern I showed is related to interpolation. 
Now I apply the threshold in the original space, and resample the mask with nearest interpolation.
The current version should work nicely, without any grey voxel.

Another big area of work: I have simplified and modularized the code.
Next step is to try to merge all the modules that are not directly relevant to brainsprite in separate PR.
I may also move some of the brainsprite-specific modules in another file, e.g. js_utils. 

Still a WIP, but it is progressing.

--- Comment 19 by GaelVaroquaux ---
Great! Things are moving forward. Thanks a lot.

I think that an important item that's remaining is avoiding the downgrade of jquery.

You have some failing tests on travis that look like they are legitimate, and related to your PR.

Also, you should rebase (or merge) on master as it will fix problems in CircleCIs. 

--- Comment 20 by jeromedockes ---
> The current version should work nicely, without any grey voxel

Indeed it does

![screenshot from 2018-10-11 08-28-56](https://user-images.githubusercontent.com/9196501/46784807-d5dd3080-cd2f-11e8-9602-9cc30748f93b.png)


--- END ---