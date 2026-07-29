# ENH: Expanding functionality for mixed source spaces and source estimates (#1462)
URL: https://github.com/mne-tools/mne-python/pull/1462
State: closed | PR: YES
Comments: 128 | Created: 2014-07-24T18:32:47Z | Closed: 2014-08-14T17:37:02Z

## Body (first 1000 chars)


## Comments

--- Comment 1 by leggitta ---
@Eric89GXL @agramfort @mluessi did I setup this pull request right?


--- Comment 2 by larsoner ---
Looks reasonable, don't forget to add a test. PR looks correct, yeah.


--- Comment 3 by leggitta ---
great, will do. will also be adding functionality for exporting to nifti shortly.


--- Comment 4 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/1003536/badge)](https://coveralls.io/builds/1003536)

Coverage remained the same when pulling **a398f416ecae747171d0d70aa31d5f4a331b6529 on leggitta:mixed_source_space** into **6447a9d019b0cbcd44101fe753eeec3646bf0b4e on mne-tools:subcortical**.


--- Comment 5 by leggitta ---
Added a method for exporting just the volume source estimates within a mixed source estimate to nifti file. Looks like the voxels line up nicely and you can even see an erp at some voxels.

![screenshot from 2014-07-25 10 16 58](https://cloud.githubusercontent.com/assets/1099867/3705476/9790e13c-141f-11e4-83f8-a8275afc35eb.png)

But it looks like most of the signal is coming from noise?

![screenshot from 2014-07-25 10 17 25](https://cloud.githubusercontent.com/assets/1099867/3705475/978f3bf2-141f-11e4-88a6-82886d2938ac.png)

These data are from the left auditory evoked response. 


--- Comment 6 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/1007507/badge)](https://coveralls.io/builds/1007507)

Coverage remained the same when pulling **08a178a3a0f3079401c7952735a285cadf5a529a on leggitta:mixed_source_space** into **6447a9d019b0cbcd44101fe753eeec3646bf0b4e on mne-tools:subcortical**.


--- Comment 7 by larsoner ---
So now we can export a whole-brain volume to NIFTI, and sub-volumes to NIFTI. You going to work on surfaces to NIFTI next? Then the to-NIFTI method could be part of the `BaseSourceEstimate` class because it should be able to work on any type. (Discrete would be a lot like the surfaces, it would just use the `rr` parameter.)


--- Comment 8 by leggitta ---
Yes. I'm currently figuring out how to incorporate surfaces into nifti as a method of `MixedSourceEstimate`, but it would make sense to incorporate into `BaseSourceEstimate`.


--- Comment 9 by leggitta ---
Ok, I updated `MixedSourceEstimate.export_volumes_to_nifti` to include an option to export the surface activations as well. Below is the same source estimate plotted via both methods. They look lined up to me.

One obstacle to using this as a method in `BaseSourceEstimate` is that I do need a whole-brain grid established, which would need to be generated for a surface source estimate.

![screenshot from 2014-07-28 16 57 26](https://cloud.githubusercontent.com/assets/1099867/3728945/3773d6f6-16b3-11e4-8186-3e59c530546b.png)
![screenshot from 2014-07-28 16 55 53](https://cloud.githubusercontent.com/assets/1099867/3728947/3c09aa38-16b3-11e4-88b3-9901aab4dbdb.png)


--- Comment 10 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/1016947/badge)](https://coveralls.io/builds/1016947)

Coverage remained the same when pulling **8cb8a0f8178eb04d0c7c114a311bc6662efa6ace on leggitta:mixed_source_space** into **6447a9d019b0cbcd44101fe753eeec3646bf0b4e on mne-tools:subcortical**.


--- Comment 11 by larsoner ---
Ahh, right. Looks good! I think that you shouldn't need the whole-brain grid for surfaces / discrete source spaces, since they by definition do not exist on a regular (subset of a whole-brain) grid. Did you end up having to upsample to the high-resolution surfaces and then map those points into the 1mm voxel space, or did you do something else? (I don't have quite enough time right now to look through the code to figure it out...)


--- Comment 12 by leggitta ---
Here I took each surface vertex and found it's nearest neighbor in the volume grid (in this case, a grid with 5 mm spacing). If a grid point had more than one vertex 'assigned' to it, I took the average of those vertices. 

I'd like to add the option of using the full MRI resolution, but in this case I figured I'd use the spacing given by the volume sources. 


--- Comment 13 by leggitta ---
Ok, I still need to add support for `dest` and `mri_resolution` arguments


--- Comment 14 by agramfort ---
> Ok, I still need to add support for dest and mri_resolution arguments

may the force be with you :)


--- Comment 15 by leggitta ---
If I have overlapping elements from two interpolation matrices (of type `csr_matrix`) from two adjacent brain regions, do I take the average value? I tried adding them together, but it gave me messy results.


--- Comment 16 by larsoner ---
Yeah, averaging would make the most sense. Eventually we might want a
weighted average of some sort, but a regular average should work for now.

Eric


--- Comment 17 by mluessi ---
Looks good so far :). We should find out how FreeSurfer `mri_surf2vol` does the interpolation, I assume it does something smart. 


--- Comment 18 by leggitta ---
Good idea. I was about to try generating an interpolation matrix for the surface. My latest attempt to map each surface vertex to the nearest voxel seems to have failed. 

![screenshot from 2014-07-31 13 12 59](https://cloud.githubusercontent.com/assets/1099867/3770934/2b2a7bd6-18f0-11e4-9a9a-d79c0f8e8c21.png)


--- Comment 19 by leggitta ---
Is the freesurfer source code available online?


--- Comment 20 by larsoner ---
Did you check this website? :)

http://lmgtfy.com/?q=freesurfer+source+code

Specifically, you'd be interested in bullet "2. Open Source Distribution". It looks like you'll need to download it to your computer to browse it, unless you have a CVS client that can browse remote repos (one probably exists, but I've never looked for it).


--- END ---