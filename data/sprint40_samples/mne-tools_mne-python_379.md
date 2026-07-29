# WIP: MRI/Head Coregistration / Scaling FsAverage (#379)
URL: https://github.com/mne-tools/mne-python/pull/379
State: closed | PR: YES
Comments: 130 | Created: 2013-01-13T22:51:33Z | Closed: 2013-09-14T17:06:35Z

## Body (first 1000 chars)
Following up on https://github.com/mne-tools/mne-python/issues/369

Open Issues:
- FIX
  - For scaling, allow the bem file to have a different name from fsaverage 
- TESTs
  - try to add TESTs for the GUI through traits
- DOC
  - integrate the documentation page
- ENH
  - set the qt backend as default for traitsui
- ENH (possibly for the future)
  - create source space before scaling


## Comments

--- Comment 1 by christianbrodbeck ---
@dengemann mentioned Head-MRI coregistration (https://github.com/mne-tools/mne-python/pull/366#issuecomment-12204704). I also made a traits GUI for that and I can add it to this PR since it's very similar to scaling fsaverage. The main issue I encountered was that the fit requires the fiducials as an initial constraint, and fiducials do not exist for MRI files. Since I did not find a good way with a traits UI to switch back and forth between two tasks (setting fiducials and fitting) I made a separate GUI for creating a fiducials file first. Maybe there is a better way to do this? I can add the two GUIs here as a basis for discussion.


--- Comment 2 by christianbrodbeck ---
@agramfort 
I started expanding transform into a package to include the coregistration related code. Before I start also moving tests etc., do you agree with this structure?


--- Comment 3 by agramfort ---
fine with me.

for me to follow where you're heading can you describe a workflow / code to use what you wrote? A kind of draft of doc to make sure I agree with the philosophy?


--- Comment 4 by christianbrodbeck ---
@agramfort Could you have a look at what I added to transforms.py (https://github.com/mne-tools/mne-python/pull/379/files#diff-4), whether you would prefer this to be somewhere else.

For the coregistratrion, a first implementation is in place, although I still want to clean it up. The fsaverage folder has to contain all necessary MRI files as well as the fiducials file from the mne download. Then, there are these two options:

```
path = mne.datasets.sample.data_path()
raw_file = path + '/MEG/sample/sample_audvis_raw.fif'
subjects_dir = path + '/subjects'

# without GUI
from mne.transforms import coreg
c = coreg.MriHeadFitter(raw_file, s_from='fsaverage', s_to='fsa_sc', subjects_dir=subjects_dir)
c.plot() # creates a mayavi figure that dynamically updates
c.set_nasion(0,8,0) # correct the position of the nasion
c.fit()
c.save() # save the scaled brain and the trans file

# with GUI
import mne.transforms.coreg_gui as gui
gui.MriHeadCoreg(raw_file, s_from='fsaverage', s_to='fsa_sc', sub

--- Comment 5 by agramfort ---
> @agramfort Could you have a look at what I added to transforms.py (https://github.com/mne-tools/mne-python/pull/379/files#diff-4), whether you would prefer this to be somewhere else.

fine there. Besides the use of np.matrix

> For the coregistratrion, a first implementation is in place, although I still want to clean it up. The fsaverage folder has to contain all necessary MRI files as well as the fiducials file from the mne download. Then, there are these two options:
> 
> path = mne.datasets.sample.data_path()
> raw_file = path + '/MEG/sample/sample_audvis_raw.fif'
> subjects_dir = path + '/subjects'
> 
> # without GUI
> 
> from mne.transforms import coreg
> c = coreg.MriHeadFitter(raw_file, s_from='fsaverage', s_to='fsa_sc', subjects_dir=subjects_dir)
> c.plot() # creates a mayavi figure that dynamically updates
> c.set_nasion(0,8,0) # correct the position of the nasion
> c.fit()
> c.save() # save the scaled brain and the trans file
> 
> # with GUI
> 
> import mne.transforms.core

--- Comment 6 by christianbrodbeck ---
> so this creates in subjects_dir a new subject called fsa_sc? with all
> the necessary files for MNE?

Yes, should, although I am not sure if I am considering all the possibilities yet.


--- Comment 7 by christianbrodbeck ---
Here's an update on the coregistration GUIs. Let me know if you think this should be prepared for potential inclusion. The fitting is done by functions that are already separate or that could be extracted if they would be useful independent of the GUI.

Fitting an MRI to a head:

```
>>> MriHeadCoreg('path/to/R0242_raw.fif', s_from='fsaverage')
```

![Screen Shot 2013-02-08 at 00 27 44 ](https://f.cloud.github.com/assets/145771/138540/a70b979a-71b1-11e2-8fff-8a43b4173cd0.png)

Fitting a head to an existing MRI requires fiducials, which can be generated using this GUI:

```
>>> Fiducials('R0273')
```

![Screen Shot 2013-02-08 at 00 33 45 ](https://f.cloud.github.com/assets/145771/138545/e30d289e-71b1-11e2-9da2-373b30ef7d60.png)

Then the head-mri coregistration can be done:

```
>>> HeadMriCoreg('path/to/R0273_raw.fif')
```

![Screen Shot 2013-02-08 at 00 35 23 ](https://f.cloud.github.com/assets/145771/138546/19b60d98-71b2-11e2-9d8f-0ddaa45fa463.png)


--- Comment 8 by agramfort ---
my review is not done but I just tried with the sample data and got:

No such file or directory: '/Users/alex/work/data/subjects/fsaverage/bem/fsaverage-head.fif'

should we ship the fsaverage-head.fif with the sample data?


--- Comment 9 by christianbrodbeck ---
Yes the fsaverage in the sample data set has an empty bem directory. `mne.transforms.coreg.find_mri_paths()` looks for all the files that are needed.


--- Comment 10 by mluessi ---
I just tried, it it seems to work quite well. Nice job :-). Two things:
- How does the fitting procedure compare to what MNE does? @mshamalainen told me that MNE is trying to keep the nasion at a constant location while rotating the rest of the points (not sure how it is done exactly). Also, he told me that the fitting procedure is matching the dig. points to the head surface between the vertices (which is not simple to do) but I guess if you use a high-res surface then this is less important.
- I think it would be good to make the GUI's more scriptable, e.g., it would be good if instead of just the a raw file name, measurement info could be passed and it should be possible to change the trans file name being written (as a parameter to HeadMriCoreg). This will make it easier to create custom pipelines.


--- Comment 11 by mluessi ---
One more thing.. in `HeadMriCoreg` I think it would be nicer if the head surface had some transparency and the digitization points were displayed as points instead of a mesh. Like that it would be easier to see how close the points are to the surface (or so I think).


--- Comment 12 by christianbrodbeck ---
@agramfort 

> can you write a quick how to (step be step) starting from the clean sample data?

I'll do that

@mluessi 

> How does the fitting procedure compare to what MNE does

The nasion is kept constant (you can manually adjust it before running the fit). The fit uses scipy leastsq to minimize the distance from each digitizer head shape point to the closest mri point. Alternatively the head mri coregistration utility can use just the LAP/RAP fiducials.

> matching the dig. points to the head surface between the vertices

The fiducials utility currently places the fiducials only to vertex locations (that's what Mayavi offers). In case that's not accurate enough I included the fields for manually adjusting the coordinates

> I think it would be good to make the GUI's more scriptable

Definitely

> in `HeadMriCoreg` I think it would be nicer if the head surface had some transparency and the digitization points were displayed as points instead of a mesh. Like that it would be easier 

--- Comment 13 by mluessi ---
@christianmbrodbeck  FYI the following point matching method is implemented in MNE (thanks @mshamalainen ):

"Besl, P., & McKay, N. (1992). A method for registration of 3-D shapes. IEEE Trans PAMI"

The method implemented here seems to be optimizing them same objective function, but I wonder if there are any guarantees that it converges to the same solution.


--- Comment 14 by christianbrodbeck ---
Re quick how to: [Here](https://dl.dropbox.com/u/659990/mne-python/html/python_manual.html) is a draft for a manual page. Currently, `mne_setup_forward_model` is called right after scaling the mri, but only for the ico subdivision method.

Strangely automatic alignment of the sample dataset head always ends up crooked, but that's not a problem I had with my own subjects...

@mluessi thanks for the info, I don't know to what degree one could make the methods converge by customizing the `leastsq` call...


--- Comment 15 by agramfort ---
nice !

quick feedback on usability:
- as a user it would like to know where the trans file is saved as
  well as the fiducial coordinates.
- why two GUIs? ie set first fiducials and then do the coreg? the
  mne_analyze way would be to do both in one step and initialize the fit
  with the fiducials.
- the section "Subjects without MRI" suggests that the copying could
  be done automatically. mne.create_default_subject?
- I would name mne.gui.coregister_head_to_mri just mne.gui.coregister
  or mne.gui.coregistration
- mne_analyze has a way to discard dig points that are way off. Would
  be neat to have this too.

Also I've seen some code relative to the forward modeling. I think
this should be independent from the coreg step.


--- Comment 16 by christianbrodbeck ---
> - as a user it would like to know where the trans file is saved as well as the fiducial coordinates.

I was planning to make arguments with templates as default, such as `"{raw_dir}/{subject}-trans.fif"` 

> - why two GUIs? ie set first fiducials and then do the coreg? the mne_analyze way would be to do both in one step and initialize the fit with the fiducials.

That would be preferable but would require me to spend some more time with traits and co ... yes for the long term  though

> - the section "Subjects without MRI" suggests that the copying could be done automatically. mne.create_default_subject?

You mean pulling the data from your mne and freesurfer application folders and running the setup? I can look into that.

> - I would name mne.gui.coregister_head_to_mri just mne.gui.coregister or mne.gui.coregistration

I'll go with `coregistration` unless there is opposition to that?

> - mne_analyze has a way to discard dig points that are way off. Would be neat to have this too.


--- Comment 17 by agramfort ---
> I was planning to make arguments with templates as default, such as
> "{raw_dir}/{subject}-trans.fif"

+1

> why two GUIs? ie set first fiducials and then do the coreg? the
> mne_analyze way would be to do both in one step and initialize the fit with
> the fiducials.
> 
> That would be preferable but would require me to spend some more time with
> traits and co ... yes for the long term though

good we agree :)

> You mean pulling the data from your mne and freesurfer application folders
> and running the setup? I can look into that.

yes do the necessary copies automatically.

> I would name mne.gui.coregister_head_to_mri just mne.gui.coregister or
> mne.gui.coregistration
> 
> I'll go with coregistration unless there is opposition to that?

+1

> It's only the preparatory setup_forward_model. You don't think that should
> be done automatically?

I don't think we should as not everybody uses the same parameters.

I would follow the mne workflow and add an mne.setup_forward_model
lik

--- Comment 18 by christianbrodbeck ---
> mne.setup_forward_model

Yes you're right, there are too many parameters


--- Comment 19 by dengemann ---
Btw. as we are at it how is it going here? I was already about to ask for it ;-)


--- Comment 20 by christianbrodbeck ---
Feel free to try it and let me know what you think :) updated manual page is [here](https://dl.dropbox.com/u/659990/mne-python/html/python_manual.html) but does not reflect the fact that fiducials can now be set in the same GUI. 

I'm working on the exclusion of head shape points.

Current layout:
![Screen Shot 2013-03-31 at 6 54 50 PM](https://f.cloud.github.com/assets/145771/322492/0d51ec94-9a56-11e2-9053-0ef05e11d9f6.png)


--- END ---