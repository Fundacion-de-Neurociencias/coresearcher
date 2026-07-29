# ENH Concatenated epoch plot (#2154)
URL: https://github.com/mne-tools/mne-python/pull/2154
State: closed | PR: YES
Comments: 303 | Created: 2015-05-27T12:17:24Z | Closed: 2015-06-16T07:34:43Z

## Body (first 1000 chars)
Sorry for the delay. I'll make up for it over the weekend.
This works at least on my computer for displaying the first few of the epochs. The scrollbars are under construction.

TODOs
- [x] keyboard shortcuts
- [x] dropping bad epochs
- [x] deprecate old `plot` function
- [x] scale data using `pageup` and `pagedown` keys (for both raw and epochs)
- [ ] make epochs dropping work for `preload=False`
- [x] mark bad epochs in scrollbar
- [x] update example
- [ ] mark bad channels ? 
- [x] red border for bad epochs instead of shading
- [x] add button for projector
- [x] add vertical lines to show event color in epochs

BUGS
- [x] tight_layout on macosx
- [x] projs
- [x] no legend
- [x] vertical line at t=0 won't work if epoch is from tmin > 0


## Comments (first 1000 chars each)

--- Comment 1 by mainakjas ---
Awesome, thanks @jaeilepp for making the PR :)


--- Comment 2 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/2669842/badge)](https://coveralls.io/builds/2669842)

Coverage decreased (-0.36%) to 90.38% when pulling **5827a8e7d32a3a63eb02338685da182fb72fb486 on jaeilepp:concatenated_epoch_plot** into **66fbe3ba74da75727233e491d4dc88eb3109cc22 on mne-tools:master**.


--- Comment 3 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/2669940/badge)](https://coveralls.io/builds/2669940)

Coverage decreased (-0.36%) to 90.38% when pulling **5827a8e7d32a3a63eb02338685da182fb72fb486 on jaeilepp:concatenated_epoch_plot** into **66fbe3ba74da75727233e491d4dc88eb3109cc22 on mne-tools:master**.


--- Comment 4 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/2679485/badge)](https://coveralls.io/builds/2679485)

Coverage decreased (-0.14%) to 90.59% when pulling **7df67ebc02cf3163fffa3d94c1685e8db3f1e8bc on jaeilepp:concatenated_epoch_plot** into **66fbe3ba74da75727233e491d4dc88eb3109cc22 on mne-tools:master**.


--- Comment 5 by mainakjas ---
Good start @jaeilepp . Some quick comments:
- we should have a way to browse the epochs using keyboard shortcuts (arrow keys?)
- title looks buggy right now. This is what I see:

![epochs_viewer](https://cloud.githubusercontent.com/assets/3817535/7881779/cf5dfad0-0606-11e5-9a2b-7577fec06643.png)


--- Comment 6 by mainakjas ---
I can't seem to select bad channels here. I think we want to retain that functionality :)


--- Comment 7 by mainakjas ---
If I resize the window, the x axis tick labels disappear under the scrollbar. Maybe that needs to be fixed.


--- Comment 8 by mainakjas ---
@dengemann @fraimondo you should give it a try!


--- Comment 9 by mainakjas ---
Let us know when you've addressed the comments. It's a great start. Thanks @jaeilepp 


--- Comment 10 by mainakjas ---
One last thing. Can you also update an example so that people can try it out easily? Thanks


--- Comment 11 by jaeilepp ---
I reused a lot of the code just to make the initial plotting work. It has already changed a bit. Also, the code conforms to the old conventions this way.


--- Comment 12 by mainakjas ---
On ipython notebook, I get the following error:

``` py
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-36-8b72c3001d45> in <module>()
----> 1 epochs.plot_concat()
      2 #epochs.drop_bad_epochs()
      3 #fig = epochs.plot_drop_log();

/home/mainak/Desktop/projects/mne-python/mne/epochs.pyc in plot_concat(self, picks, scalings, n_epochs, n_channels, title_str, show, block)
    543         return plot_epochs_concat(self, picks=picks, scalings=scalings,
    544                                   n_epochs=n_epochs, n_channels=n_channels,
--> 545                                   title_str=title_str, show=show, block=block)
    546 
    547     def plot_psd(self, fmin=0, fmax=np.inf, proj=False, n_fft=256,

/home/mainak/Desktop/projects/mne-python/mne/viz/epochs.py in plot_epochs_concat(epochs, picks, scalings, n_epochs, n_channels, title_str, show, block)
    627     plt

--- Comment 13 by mainakjas ---
I added important TODOs at the top of the page. Feel free to edit it / add more stuff and check the boxes as you address them.


--- Comment 14 by mainakjas ---
Is there a keyboard shortcut to scale the data along the y-axis? Say `pageup` and `pagedown`. I think we should have that too in case the user is not satisfied with the default scaling. Thoughts @dengemann @Eric89GXL ? Could be another PR if it needs to be updated in `raw.plot()` too


--- Comment 15 by larsoner ---
@choldgraf has requested that for raw plotting, +1 for adding it to both places, and I like page-up and page-down. Shouldn't be too difficult -- a multiplicative factor of 1.25, 1.5, or 2 should work.


--- Comment 16 by choldgraf ---
Another thing I've seen implemented is just to have an options box pop up when you press a certain key, then you can type in whatever new number you want and if it's different from the old number, then the data are re-plotted.


--- Comment 17 by choldgraf ---
Actually while I'm at it, there's a naming inconsistency in the mne.viz section. These are two functions:

```
viz.plot_evoked_image
viz.plot_image_epochs
```

I feel like it should be consistent (and my preference would be to rename it to `plot_epochs_image`) 


--- Comment 18 by mainakjas ---
... maybe not an options box because it's just slower for the user and I doubt they'd want such fine-grain control. That can be achieved anyway from the scripting mode.


--- Comment 19 by choldgraf ---
+1 to not including it, just a point of information :)


--- Comment 20 by mainakjas ---
@choldgraf can you raise an issue about the naming inconsistency so that we can discuss it there?


--- END ---