# [MRG+1] Enable computation of vector surface source estimates (#3842)
URL: https://github.com/mne-tools/mne-python/pull/3842
State: closed | PR: YES
Comments: 88 | Created: 2016-12-13T12:00:42Z | Closed: 2017-08-18T13:37:57Z

## Body (first 1000 chars)
picking this up from #3240 

The source space that is used for the inverse computation defines a set of dipoles, distributed across the cortex. When visualizing a source estimate, it is sometimes useful to show the dipole directions, as well as their estimated magnitude.

For example, for educational purposes. Here is the effect of the `loose` parameter on the sample dataset:

(click image to zoom in)
![image3398](https://cloud.githubusercontent.com/assets/428273/21139612/6c8471f8-c13c-11e6-9edd-8a3484f67d5b.png)

TODO:
- [x] `pick_ori='vector'` is supported in all cases
- [x] `VectorSourceEstimate` has all of the functionality of a regular `SourceEstimate`
- [x] `.magnitude()` and `.normal()` methods to convert to a regular `SourceEstimate` object
- [x] Saving only to HDF5 format
- [x] Full unit-test coverage
- [x] Example
- [x] Tutorial 
- [x] Plotting function that uses PySurfer
- [x] Make timeviewer work
- [x] Address @Eric89GXL 's comments
- [x] Make Travis hap

## Comments

--- Comment 1 by larsoner ---
cc @SherazKhan do you have a small script you could share showing full source activation?

--- Comment 2 by wmvanvliet ---
see the example script.

--- Comment 3 by larsoner ---
@wmvanvliet I know I see yours. But I know @SherazKhan has something similar, so it would be good to "compare notes" as to what sort of viz we can make

--- Comment 4 by larsoner ---
Removing a file naming requirement (making the check less strict) wouldn't
really be an API change. It shouldn't break anyone's code unless they do
something very strange/rare like rely on the error or warning


--- Comment 5 by larsoner ---
I still think it's best to use a Brain. It has lots of nice stuff, even if
some of it doesn't apply. But if you don't want to do it I can take over
the PR. I'd rather not merge this into master with the aim to change it to
use Brain, because that would be a backward incompatible change (both the
visual output and return type would change substantially).

On Jan 2, 2017 9:55 AM, "Marijn van Vliet" <notifications@github.com> wrote:

> *@wmvanvliet* commented on this pull request.
> ------------------------------
>
> In mne/viz/_3d.py <https://github.com/mne-tools/mne-python/pull/3842>:
>
> > +    def _plot_hemi_mesh(src, hemi_ind):
> +        """Plot the mesh of a single hemisphere"""
> +        with warnings.catch_warnings(record=True):  # FutureWarning in traits
> +            if high_resolution:
> +                tris = src[hemi_ind]['tris']
> +            else:
> +                tris = src[hemi_ind]['use_tris']
> +
> +            # Plot mesh
> +            mlab.triangular_mesh(src[

--- Comment 6 by wmvanvliet ---
I'll give PySurfer a shot tomorrow.

--- Comment 7 by codecov-io ---
# [Codecov](https://codecov.io/gh/mne-tools/mne-python/pull/3842?src=pr&el=h1) Report
> Merging [#3842](https://codecov.io/gh/mne-tools/mne-python/pull/3842?src=pr&el=desc) into [master](https://codecov.io/gh/mne-tools/mne-python/commit/2fd1241562e4086f6ae046994ff568af3e086817?src=pr&el=desc) will **increase** coverage by `0.02%`.
> The diff coverage is `91.16%`.


```diff
@@            Coverage Diff            @@
##           master   #3842      +/-   ##
=========================================
+ Coverage   83.58%   83.6%   +0.02%     
=========================================
  Files         349     349              
  Lines       64978   65170     +192     
  Branches    10047   10083      +36     
=========================================
+ Hits        54311   54485     +174     
- Misses       7827    7831       +4     
- Partials     2840    2854      +14
```




--- Comment 8 by wmvanvliet ---
@Eric89GXL check it out! Plotting with PySurfer :)

--- Comment 9 by larsoner ---
There are some docstring style issues:

https://travis-ci.org/mne-tools/mne-python/jobs/204941247#L3103

If it's ready for merge from your end please re-title as MRG so I can add my +1 :)

--- Comment 10 by larsoner ---
In case anyone wants to see the example output, it's here:

https://3868-1301584-gh.circle-artifacts.com/0/home/ubuntu/mne-python/doc/_build/html/auto_examples/inverse/plot_vector_mne_solution.html

@agramfort do you want to look again? Or @jaeilepp since you work on viz a lot?


--- Comment 11 by larsoner ---
@SherazKhan last call to potentially integrate your code here :)

--- Comment 12 by larsoner ---
@wmvanvliet any time to do the last little tweaks so we can get it into 0.14?

I can also fix the last few little things and merge if you don't have time

@agramfort @jaeilepp time for another set of eyes?

--- Comment 13 by agramfort ---
please give me time to look.


--- Comment 14 by jaeilepp ---
How easy would it be to add ``time_viewer`` option to the plotter?

--- Comment 15 by larsoner ---
@wmvanvliet hoping to release 0.14 soon if possible. Should delay this to the next release (0.15)? It might be a good idea, that way people can test a bit more extensively in `master` before release.

--- Comment 16 by wmvanvliet ---
that is a good idea. Especially since the functionality needs to be integrated in further PRs. For example the `apply_forward` function needs to be able to handle a `VectorSourceEstimate` object.

--- Comment 17 by agramfort ---
ok let's wait a bit then.


--- Comment 18 by wmvanvliet ---
> How easy would it be to add time_viewer option to the plotter?

Easy if I would subclass the `TimeViewer`. Let me give it a try.

--- Comment 19 by wmvanvliet ---
Ah, but to do it properly, I actually need to override `Brain.set_data_time_index`. Then thinks like `save_image_sequence` would also work. 

--- Comment 20 by wmvanvliet ---
I give up. Cannot make `time_viewer` or `brain.set_time` work or find a clean PR for pysurfer to make it work. @Eric89GXL help?

--- END ---