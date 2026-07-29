# Enh/surface plotting2 (#1016)
URL: https://github.com/nilearn/nilearn/pull/1016
State: closed | PR: YES
Comments: 111 | Created: 2016-02-25T19:32:11Z | Closed: 2017-02-23T17:49:22Z

## Body (first 1000 chars)
Adding surface visualization along with example and data fetcher for NKI enhanced surface data.


## Comments (first 1000 chars each)

--- Comment 1 by AlexandreAbraham ---
Juste after I left, you gotta be kidding me :D


--- Comment 2 by KamalakerDadi ---
Example looks great. Just minor details on example `plot_surf_stat_map`


--- Comment 3 by GaelVaroquaux ---
@juhuntenburg : if I look at one of your images, you have a huge amount of not useful whitespace around a brain:

https://circle-artifacts.com/gh/nilearn/nilearn/1298/artifacts/0/home/ubuntu/nilearn/doc/_build/html/_images/sphx_glr_plot_surf_stat_map_004.png

We need to do something about this.


--- Comment 4 by juhuntenburg ---
Yes I agree about the white space. My colleague uses another function to crop the image and combine medial and lateral view into one display: https://github.com/soligschlager/brainsurfacescripts/blob/temp/plotting.py#L343-L420 Would some version of that be an option? Then I would look into it with her. 

Or I will check whether it is possible to avoid the white space in matplotlib in the first place


--- Comment 5 by GaelVaroquaux ---
> the image and combine medial and lateral view into one display: https://
> github.com/soligschlager/brainsurfacescripts/blob/temp/plotting.py#L343-L420
> Would some version of that be an option?

Hum, that solution isn't great: it saves to a raster image after
reloading.

> Or I will check whether it is possible to avoid the white space in matplotlib
> in the first place

That should be possible. In the volumetric plotting code we compute the
bounds of the objects that we plot, and we use them to adapt the bounds
of the plot.


--- Comment 6 by KamalakerDadi ---
Hi @juhuntenburg Any progress on this ?


--- Comment 7 by juhuntenburg ---
Hi @KamalakerDadi: ah yes, good reminder.
1. White space around the figure:
   I looked into this but didn't find a solution yet. In the volumetric plotting code, I figure this is the step to adapt the bounds: https://github.com/nilearn/nilearn/blob/master/nilearn/plotting/displays.py#L92-L94 ? 
   But since I don't use imshow here I don't see how to translate it directly. I tried to change the bounding box of the 3d axis with ax.set_clip_box but it didn't help. Maybe one of you has an idea that they could point me to?
2. Example / documentation: 
   I would like to replace the example which plots an arbitrary volume of a time series with one that plots seed-based connectivity of the example dataset. I will look into this asap and then also write a proper documentation of the example. 

Are there any other crucial points for now?


--- Comment 8 by KamalakerDadi ---
Thanks @juhuntenburg 

> White space around the figure:

I will try to search for some solutions/hints.

> Example / documentation: 

yes, please. It looks interesting.


--- Comment 9 by juhuntenburg ---
I have reworked the example. For this the Destrieux parcellation (shipped with Freesurfer) would need to be added to the Nilearn NKI dataset. For testing you can find the file here: https://www.dropbox.com/s/j66g4ljqaj5hz3a/lh.aparc.a2009s.annot?dl=0
Happy for feedback!


--- Comment 10 by juhuntenburg ---
I also want to make a second function plot_surf_roi (very similar just using the median instead of mean value for the face color and some other defaults) and display the seed region as well.


--- Comment 11 by GaelVaroquaux ---
> I have reworked the example. For this the Destrieux parcellation (shipped with
> Freesurfer) would need to be added to the Nilearn NKI dataset.

I am +1 adding the Destrieux parcellation, but in a different dataset,
and with a different downloader. Ideally, we should also be able to have
an example plotting it.


--- Comment 12 by GaelVaroquaux ---
> I also want to make a second function plot_surf_roi (very similar just using
> the median instead of mean value for the face color and some other defaults)

I am not sure that I understood what this function does, and its purpose.
Would you mind detailling a little more. Cheers.


--- Comment 13 by juhuntenburg ---
The current function is not ideal for plotting labels (atlas, roi) because it interpolates the values and doesn't create clean borders. This can easily be changed by using the median value instead of the mean to calculate the face colors. 
Does that make more sense?


--- Comment 14 by GaelVaroquaux ---
> The current function is not ideal for plotting labels (atlas, roi) because it
> interpolates the values and doesn't create clean borders. This can easily be
> changed by using the median value instead of the mean to calculate the face
> colors.
> Does that make more sense?

It makes more sense in terms of the purpose. However, the median value
surprised: if those are labels, than the mode should be used, rather than
the median (ie the label number that is most represented). Now, I realize
that if we are talking triangles, there are only three values, in which
case, either the mode is undefined, or it is equal to the median.


--- Comment 15 by KamalakerDadi ---
Can you please rebase and resolve the conflicts ?

I can review your PR again this week.


--- Comment 16 by juhuntenburg ---
Yes of course, just quick question to be on the save side: I updated my master and then rebased the surface plotting branch to master. Now when I want to push the rebased branch to its remote I would need to do push --force because it cannot fast-forward anymore. Is it ok to do that or is there a better way?


--- Comment 17 by juhuntenburg ---
@GaelVaroquaux: would you suggest adding the Destrieux dataset fetcher, an atlas plotting version of the plotting function and an example in this PR or can it wait for later? I could also avoid using the atlas in the current example and just hard code the seed labels.


--- Comment 18 by bthirion ---
Yes, in that case you push --force. 
Thanks for keeping this PR alive ! 


--- Comment 19 by juhuntenburg ---
Done, thanks @bthirion !


--- Comment 20 by GaelVaroquaux ---
> Now when I want to push the rebased branch to its remote I would need
> to do push --force because it cannot fast-forward anymore. Is it ok to
> do that or is there a better way?

It's OK, it's your own private branch


--- END ---