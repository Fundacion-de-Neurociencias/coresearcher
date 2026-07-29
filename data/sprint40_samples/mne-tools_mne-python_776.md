# ENH: Forward solution in python (#776)
URL: https://github.com/mne-tools/mne-python/pull/776
State: closed | PR: YES
Comments: 143 | Created: 2013-09-23T18:24:52Z | Closed: 2013-10-21T19:30:46Z

## Body (first 1000 chars)
This code now produces similair results in Python as in C, with computation time faster for `oct-6` source spaces on my machine. Should be ready for review, and hopefully extensive testing to make sure there aren't issues across different machines, installs, etc.


## Comments

--- Comment 1 by mluessi ---
Nice, you are too fast :). I'm looking forward to trying to understand the code, it's always an interesting challenge ;). 


--- Comment 2 by larsoner ---
So far I haven't done any crazy efficiency manipulations, so all the understanding is really just trying to understand Matti's code, which is a different kind of challenge :) I wanted to construct something that worked first, and then start optimizing. Unfortunately the field computation matrix is too much of a bottleneck for me to debug the rest of the code (computing at source locations), so that will probably need to be optimized before continuing. I figured I'd post the WIP in case you wanted to do some hacking, too.


--- Comment 3 by mluessi ---
Have you read the BEM section in Matti's 1993 paper? This code essentially implements the computation of the integrals described there. I will go back and (re) read the paper, I think it will help with getting a better understanding of the code. 


--- Comment 4 by larsoner ---
@mluessi I sped up the field computation code using the same trick that I used for `_accumulate_normals`, maybe you can find a way to make it faster anyway. I left the original, clearer, equivalent code commented in there for clarity. Moving on now...


--- Comment 5 by larsoner ---
And to answer your other question, I have not read that paper yet.


--- Comment 6 by larsoner ---
@mluessi I just added a `fast_cross_3d` function, since `np.cross()` was a bottleneck. Turns out if you avoid the memcopy's that (I think) their code uses, then you can get a ~4x increase if you're crossing more than ~1000 vectors at a time (blue is `np.cross`, green is `mne.surface.fast_cross_3d`):

![figure_1](https://f.cloud.github.com/assets/2365790/1201360/9c4fc3ae-2533-11e3-9119-39323a88554e.png)

Turns out the forward solution code uses a bunch of cross products, so it sped the field computation matrix code up a little bit.


--- Comment 7 by larsoner ---
@agramfort @mluessi this code snippet now runs, but gives incorrect results for the solution:

```
import time
import mne
path = mne.datasets.sample.data_path()
subjects_dir = path + '/subjects'
bem = path + '/subjects/sample/bem/sample-5120-5120-5120-bem-sol.fif'
meas = path + '/MEG/sample/sample_audvis_raw.fif'
src = path + '/subjects/sample/bem/sample-oct-6-src.fif'
mri = path + '/MEG/sample/sample_audvis_raw-trans.fif'
t0 = time.time()
x = mne.do_forward_solution('sample', meas, bem=bem, src=src,
                            mri=mri, subjects_dir=subjects_dir,
                            meg=True, eeg=True, verbose=True)
print time.time() - t0
t0 = time.time()
y = mne.forward.do_forward_solution2('sample', meas, bem=bem, src=src,
                                     mri=mri, subjects_dir=subjects_dir,
                                     meg=True, eeg=True, verbose=True)
print time.time() - t0
```

The timings are `40` for the C-tools, and `126` for python. I haven't explicitly para

--- Comment 8 by larsoner ---
@dengemann I assume you're not too interested in working on forward code bug squashing and optimization :)


--- Comment 9 by dengemann ---
@Eric89GXL I am but no chance at the moment, need to promote some 'science' ;-)


--- Comment 10 by dengemann ---
@Eric89GXL maybe we will end up convincing @agramfort that Numba and Cython are debatable options, despite shipping challenges ... Those would also be great for speeding up IO as exposed in #777  (I've recently used Cython for parsing eye tracking ASCII log files with about 1.2 million lines and the speedup + memory advantage was remarkable) 


--- Comment 11 by larsoner ---
I'm going to see how well I can do by vectorization, I have a feeling I could still speed it up a bit. That being said, numba or compiled code could still end up being faster. We'll see... first I have to get it to give a correct solution :)


--- Comment 12 by larsoner ---
I'm going to hold off on doing more commits here until #781 is merged, since that PR is simpler but contains some of the functions from this PR. Once that one is merged, I'll rebase this and continue.


--- Comment 13 by larsoner ---
I now have MEG and EEG (and combined) forward solution calculations working for the sample dataset. I'll move on testing `grad` support, or maybe try to make it a little faster now.


--- Comment 14 by larsoner ---
(changes not committed here because I'm waiting for the volume source space to be settled)


--- Comment 15 by larsoner ---
Still lots to work on for this:
1. Get `grad` to work
2. Test `trans` instead of `MRI`
3. Speed up the computation
4. Add EEG sphere model code
5. Add compensation code

But at least the normal `--meg --eeg` with 3-layer and `--meg` with 1-layer both appear to now give equivalent results.


--- Comment 16 by agramfort ---
forgive my question but what's the grad option?

basically the underlying question is "what is the minimum that we need (which I think we have)?"
and why adding options and maintain it later. For what usage? For example why support a sphere
EEG model if nobody should be using it in practice?


--- Comment 17 by larsoner ---
`grad` causes it to compute the gradient of fields in addition to the normal forward. I'm fine with removing that for a first pass, and then adding that and EEG sphere model support later. It should reduce the reviewing burden substantially. I also forgot about the `fixed` option -- I'm +1 for removing that, too, since you can always convert a free orientation forward to fixed (but not vice versa) and again, we can add it later WDYT?


--- Comment 18 by agramfort ---
+1 for everything. Let's add options when we need them.


--- Comment 19 by larsoner ---
Okay, I'll get on that. Should simplify the code base quite a bit, actually.


--- Comment 20 by larsoner ---
@agramfort what about constant versus linear collocation? The sample dataset uses `linear`, should we only support that to start? I don't think we have a constant collocation BEM for testing. I'm not sure how common that is, either -- WDYT?


--- END ---