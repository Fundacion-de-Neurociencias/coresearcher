# MRG eeglab .set reader (#2676)
URL: https://github.com/mne-tools/mne-python/pull/2676
State: closed | PR: YES
Comments: 172 | Created: 2015-12-06T23:01:47Z | Closed: 2015-12-23T13:30:20Z

## Body (first 1000 chars)
closes https://github.com/mne-tools/mne-python/issues/2672

very much WIP and works only for the sample data provided by EEGLAB at the moment. If anyone has files to share, I'd be happy to try them.

TODOs
- [x] Fix scaling issue when plotting `raw`
- [x] Check if chanlocs already exists in the `set` file
- [x] Check if data already exists in the `set` file
- [x] Handle epochs data
- [x] Make it work with `.dat` file
- [x] eog topoplot


## Comments (first 1000 chars each)

--- Comment 1 by jasmainak ---
okay guys, we have `preload` option now :) Thanks to @jaeilepp for debugging help. It works when data is in a separate `fdt` file. I have to think how we can handle `preload` when it's in the `set` file itself.


--- Comment 2 by larsoner ---
Those files add ~4MB to the repo. I think I'd rather put them in the `testing` dataset to avoid repo bloat. @agramfort WDYT? What's the limit on adding files?


--- Comment 3 by larsoner ---
@jasmainak there is no way to get segments of data using `loadmat`, right? I guess if data were in MATLAB's newer HDF5 .mat files we could. But since we probably can't, I think for `preload=False` with data in the `set` file you can just throw a warning if `preload is not True` (since memmapping probably won't be easy/worth it either) and say that it will be forced to `True` since data is in the `set` file.


--- Comment 4 by jasmainak ---
@Eric89GXL I was thinking maybe we could use `io.whosemat` to query if the `eeg.data` attribute is a string or an array and then try to do an `fseek` to that location. Wdyt?


--- Comment 5 by jasmainak ---
@Eric89GXL yeah the files are large at the moment. We can replace them with smaller files when we are closer to merging. That is why it's a separate commit. I'll overwrite the commit.


--- Comment 6 by larsoner ---
We could fseek and read if you can figure out how the data are actually stored in the `.mat` file. That would be cool.


--- Comment 7 by larsoner ---
@jasmainak regarding the numpy tricks, I don't know a list of them, I think you just have to get used to paying attention to and understanding the underlying copies or views. For example, you had a line which was of the form (`b` is some constant):

```
a = np.fromfile(...) * b
```

What's going to happen is the `np.fromfile` is going to create an array, let's call it `intermediate`. After that is done, this operation occurs:

```
intermediate * b
```

which creates a new array of the same size as `intermediate` -- let's call that `final`. Finally this output is assigned to the variable name `a` with:

```
a = final
```

You thus have two variables the same size as `intermediate` in memory: `intermediate`, and `a` (a.k.a. `final). So you can hopefully see how the following two lines skip an intermediate result, and only hold one variable the size of`intermediate` in memory:

```
a = np.fromfile(...)
a *= b
```

Makes sense?


--- Comment 8 by jasmainak ---
cool thanks @Eric89GXL . Looks like we have a pretty handy blogpost by someone familiar: http://ipython-books.github.io/featured-01/


--- Comment 9 by jasmainak ---
okay, this should work for `Raw` now. I'll do the epochs reader next. @jmontoyam I'm told you have tons of files to test ;) Let me know if the raw reader works for you.


--- Comment 10 by larsoner ---
Otherwise LGTM!


--- Comment 11 by jasmainak ---
okay, added basic version of epochs reader. Not sure what we should do when an epoch is associated with more than one event. For now, we throw an error ...


--- Comment 12 by larsoner ---
You'll want to rebase now that my PR has been merged. You will also need to
explicitly set info['buffer_size_sec']=1. if you don't currently set it
(git grep and you'll see examples).


--- Comment 13 by agramfort ---
if an epoch is associated with more than one id can we use the event_id with / ?


--- Comment 14 by jasmainak ---
hmm ... but how do you set the `events` array in that case? 


--- Comment 15 by jona-sassenhagen ---
The main thing is EEGLAB has precise time points for each event. This is important for e.g. sorted ERPimage plotting. The one at zero is not fundamentally different from all others, it's just the one the data are centered around.


--- Comment 16 by larsoner ---
Don't forget to add epochs tests at some point, too. Otherwise LGTM


--- Comment 17 by jasmainak ---
for testing epochs, I need really tiny files. Does anyone have them? @jona-sassenhagen @jmontoyam ?


--- Comment 18 by jona-sassenhagen ---
How small?


--- Comment 19 by jasmainak ---
less than 100 kB preferably


--- Comment 20 by jasmainak ---
... or even less than 50 kB if possible


--- END ---