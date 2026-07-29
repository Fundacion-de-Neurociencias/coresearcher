# Trans GUI (#766)
URL: https://github.com/mne-tools/mne-python/pull/766
State: closed | PR: YES
Comments: 174 | Created: 2013-09-14T17:06:04Z | Closed: 2013-11-25T20:41:44Z

## Body (first 1000 chars)
[not ready for review, replaces https://github.com/mne-tools/mne-python/pull/379]

Open issues:
1. [x] FIX:  For scaling, allow the bem file to have a different name from fsaverage 
2. [x] TESTs:  try to add TESTs for the GUI through traits
3. [ ] DOC:  Add documentation to the Python page
4. [ ] DOC:  Document traitsui backend issue and possibly handle with automatic default selection
5. [x] scale source spaces
6. [x] wait for and use https://github.com/mne-tools/mne-python/pull/739
7. [ ] add trans-fname parameter
8. [x] load existing trans file
9. [ ] automatically load trans when selecting raw and MRI?


## Comments (first 1000 chars each)

--- Comment 1 by larsoner ---
You might want to hold off on the source space, I have a python-based pr close to merge that you could use. 


--- Comment 2 by christianbrodbeck ---
Thanks @Eric89GXL I was about to ask whether it's close enough to wait for it 


--- Comment 3 by larsoner ---
Never mind, looks like it's already in there...


--- Comment 4 by christianbrodbeck ---
Question about `mne_prepare_bem_model`: I added `mne_prepare_bem_model` as a step the GUI performs automatically based on [these instructions](https://wiki.umd.edu/meglab/index.php/MNE#With_the_.27average.27_brain). In the MNE manual I now read that `mne_forward_solution` can do the computations itself. Should I thus remove this step, or is it still useful? (For speed?)


--- Comment 5 by dengemann ---
Christian, let me know when this is ready for pulling and trial / testing ;-)


--- Comment 6 by agramfort ---
see:

https://github.com/mne-tools/mne-scripts/blob/master/sample-data/run_meg_tutorial.sh

mne_setup_source_space
mne_setup_forward_model
mne_do_forward_solution

is enough assuming you did mne_watershed_bem or mne_flash_bem before.

FYI the source space generation in python is merged.

On Sat, Sep 14, 2013 at 8:18 PM, Christian Brodbeck
notifications@github.com wrote:

> Question about mne_prepare_bem_model: I added mne_prepare_bem_model as a
> step the GUI performs automatically based on these instructions. In the MNE
> manual I now read that mne_forward_solution can do the computations itself.
> Should I thus remove this step, or is it still useful? (For speed?)
> 
> —
> Reply to this email directly or view it on GitHub.


--- Comment 7 by mluessi ---
I just used your GUI to do the alignment for a subject. It works pretty well (although I didn't try the automatic alignment, I used it for simulations with a subject that doesn't have real head shape points).

I think one improvement  that would be nice is if also the trans file name could be passed to `mne.gui.coregistration` and then it would automatically save the file when the GUI is closed (with a Yes/No dialog asking for replacing the file if it exists). I'm not sure how difficult it is to add this, but it would be nice as it would allow full scriptability of the alignment process. 


--- Comment 8 by mluessi ---
Also, if the trans file exists, the GUI should load it and use it for initial alignment.


--- Comment 9 by christianbrodbeck ---
thanks @agramfort, so as I understand `mne_prepare_bem_model` is one step in `mne_setup_forward_model`, and seemingly the step required to complete fsaverage for `mne_do_forward_solution` after scaling (I can't load and scale the bem-sol file it creates). 

How does that relate to other subjects that people might want to scale? Should I run `mne_prepare_bem_model` there too? Can I expect a bem file to be present, and can I expect it to have aspecific name?

@mluessi 

> I think one improvement that would be nice is if also the trans file name could be passed to mne.gui.coregistration and then it would automatically save the file when the GUI is closed (with a Yes/No dialog asking for replacing the file if it exists). I'm not sure how difficult it is to add this, but it would be nice as it would allow full scriptability of the alignment process.

Currently after you hit save, the scaling happens in a different thread in the background and you can keep using the same GUI, i.e. load anoth

--- Comment 10 by agramfort ---
> thanks @agramfort, so as I understand mne_prepare_bem_model is one step in mne_setup_forward_model, and seemingly the step required to complete fsaverage for mne_do_forward_solution after scaling (I can't load and scale the bem-sol file it creates).

looks like it.

> How does that relate to other subjects that people might want to scale? Should I run mne_prepare_bem_model there too? Can I expect a bem file to be present, and can I expect it to have aspecific name?

yes you should expect the files to be there with the naming conventions in :

MNE-sample-data/subjects/sample/bem/

So just replace sample by the subject name as set by freesurfer.

> @mluessi
> 
> I think one improvement that would be nice is if also the trans file name could be passed to mne.gui.coregistration and then it would automatically save the file when the GUI is closed (with a Yes/No dialog asking for replacing the file if it exists). I'm not sure how difficult it is to add this, but it would be nice as it woul

--- Comment 11 by dengemann ---
Set to 0.7


--- Comment 12 by christianbrodbeck ---
An update on testing: I haven't been successful at launching the actual GUI, but an alternative would be to separate the traits data model aspect form the GUI part. The data model (i.e., deriving output from input) could then be tested completely, but what could not be tested automatically would be actual GUI interaction. I've implemented that kind of testing on the KIT marker_gui because it's small ([coverage](https://dl.dropboxusercontent.com/u/659990/mne-python/cover_marker_gui/index.html) -- I wonder though why it looks like some functions of the GUI got called).


--- Comment 13 by dengemann ---
Fair enough! 


--- Comment 14 by larsoner ---
@christianmbrodbeck do you want to merge this for 0.7 (within three weeks), or do you think you'll need more time?


--- Comment 15 by christianbrodbeck ---
I'm still aiming for 0.7... I'm working on separating the data model from the GUI so that the data model can be tested without the necessity of running a GUI. I already did this for the kit2fiff GUI so I hope the coreg GUI should be achievable, even though it's more complex. If you think that would help I could make a separate PR for the KIT2FIFF GUI so that a separate review can start earlier? 


--- Comment 16 by larsoner ---
Up to you... I don't have a sense of which would be easier.


--- Comment 17 by dengemann ---
@christianmbrodbeck feel free to chose the way that works best for you. We're still excellent in time. about 75 % of the issues closed and still about 4 weeks to go. ++++++


--- Comment 18 by dengemann ---
@christianmbrodbeck ping what's the status here? Can we push this to be part of 0.7 (this would mean this is ready to merge in about 7 to 10 days)?


--- Comment 19 by christianbrodbeck ---
I've converted the fiducials GUI, so only the coregistration part is left, should be possible in a few days.


--- Comment 20 by christianbrodbeck ---
@Eric89GXL mne.make_forward_solution requires a `-bem-sol.fif` file, which as I understand is normally created by `mne_prepare_bem_model` as part of `mne_setup_forward_model`. Is it possible to generate this `-bem-sol.fif` file in Python yet, or do we still need the C routines there?


--- END ---