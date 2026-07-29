# get_collections fails when meta-data includes lists (#451)
URL: https://github.com/bids-standard/pybids/issues/451
State: closed | PR: NO
Comments: 38 | Created: 2019-06-24T22:12:32Z | Closed: 2019-09-12T01:51:24Z

## Body (first 1000 chars)
For me this error occurs when:

```
bids_analysis = Analysis(bids_layout, model)
bids_analysis.setup(**entities)
```

`TypeError: unhashable type: 'list'`

Looking at the traceback:

```
collections = self.layout.get_collections(self.level, drop_na=drop_na, **kwargs)
```
seems to be what's failing because in:

```
> /celery_worker/src/pybids/bids/variables/entities.py(161)get_nodes()
    159         sort_cols = [sc for sc in sort_cols if sc in set(rows.columns)]
    160         sort_cols += list(set(rows.columns) - set(sort_cols))
--> 161         rows = rows.sort_values(sort_cols)
    162         inds = rows['node_index'].astype(int)
    163         return [self.nodes[i] for i in inds]
```

In this dataaset, `rows` contains some values that are lists because of structured meta-data.

For example:
```
rows['ImageType'] 
0    [ORIGINAL, PRIMARY, FMRI, NONE, ND, NORM, MOSA]
Name: ImageType, dtype: object
```


I can't really make sense of why that requir

## Comments (first 1000 chars each)

--- Comment 1 by Shotgunosine ---
Yeah, I second this, seems like i prevents using fitlins with any dataset where you've defined slice timing.

--- Comment 2 by adelavega ---
I think downgrading to 0.8.0 may be a temporary workaround.

--- Comment 3 by Shotgunosine ---
Downgrading pybids to 0.8.0 requires downgrading fitlins to 0.4.0, which isn't necessarily the end of the world. 


--- Comment 4 by effigies ---
Since they're unhashable types, the obvious solution here is to coerce lists to `tuple`s on the way in. We could probably do this sensibly as a filter on all incoming JSON.

--- Comment 5 by tyarkoni ---
Haven't looked at it yet, but I think the issue is at database level—the indexing code will probably need to be updated to detect data structures and save the dtype as `'json'` in the `Tag` model. I'm pretty sure that doesn't already happen. So I think is a problem with any kind of structured data right now.

A more general question is how to handle nested metadata. Even if we do the above, that will still only work for one level—there won't be any provision for searching deeper keys. I think we'd talked about using the convention of `FirstLevelKey.SecondLevelKey`, but I have my reservations, and that would in any case take a little more work. But as a start, the solution above should be fine.

--- Comment 6 by effigies ---
If we need a fully hashable replacement for a JSON object:

```Python
from frozendict import frozendict

def safe_json(obj):
    if isinstance(obj, list):
        return tuple(safe_json(elem) for elem in obj)
    if isinstance(obj, dict):
        return frozendict((key, safe_json(val)) for key, val in obj.items()}
    return obj
```

--- Comment 7 by Shotgunosine ---
@effigies Nice recursive implementation. @tyarkoni Right now I don't see a use case for searching deeper keys.

Should we tweak one of the tests to have a list like @adelavega's example?


--- Comment 8 by Shotgunosine ---
@effigies, should I try to put together a PR for this and variable globing from #487 or do you think you'll have a time to do that?


--- Comment 9 by satra ---
@effigies - a side note - if the intent of hashing is to restore to previous state, this may require order preservation or other requirements. insertion order in a dict is preserved by python only as of 3.7, but supported as of 3.6 (but not guaranteed).

--- Comment 10 by effigies ---
As far as I know, we don't depend on insertion ordering, but I don't know what Pandas is doing here, hashing, really.

--- Comment 11 by effigies ---
@Shotgunosine If you have the cycles, it might be more efficient for you to propose and me to review... Otherwise, feel free to pick one and I can see if I can work on the other.

--- Comment 12 by Shotgunosine ---
I'll take a shot at #487 and see how far I can get with that

--- Comment 13 by effigies ---
@Shotgunosine Incidentally, while we should handle list metadata, `SliceTiming` should generally not be seen by FitLins, as you shouldn't expect it to work on non-preprocessed data. If you've slice-timing-corrected or head-motion-corrected, the validity of slice timing information is destroyed and should be removed from metadata.

@adelavega What's the context you were encountering this?

--- Comment 14 by Shotgunosine ---
That particular example occurred because I was setting up an analysis without passing the derivatives directory. So you're right, slice_timing shouldn't be an issue. Other random metadata coming through from the dicom may still be an issue. Let me double check to reproduce the error.


--- Comment 15 by adelavega ---
@effigies do you mean if you only set up the layout on the fmriprep outputs? I'm trying to remember which dataset this happened in, but I think it's because I set up the layout like: `BIDSLayout(raw, derivatives=preproc_dir)` (in Neuroscout, not fitlins).

So yes, I think fitlins should usually not have trouble with this. And maybe I should just change this code to only set up the `BIDSLayout` using the preproc_dir. I think I used to do it this way to emulate what fitlins (used to) do. 


--- Comment 16 by Shotgunosine ---
Yeah, now that I'm going back through my debugging from last night I think I was also only encountering this when setting up the BIDSLayout outside of fitlins. Maybe this can just be closed then?

--- Comment 17 by adelavega ---
Well, it's still a valid way to set up a `BIDSLayout` and `get_collections` has uses outside of fitlins (e.g. to get the events in a raw bids dataset), so I think it's important to fix. 

Also, can't fitlins read the original event files in a dataset, and then would encounter this problem then? Just the way I run fitlins I don't point it to the raw dataset ever.

--- Comment 18 by effigies ---
We do read the original events files. Just we don't collect metadata from the original BOLD files.

--- Comment 19 by adelavega ---
But for me this was happening simply doing `analysis.setup()`

Regardless, given you have a seemingly easy fix, it makes sense to implement.

--- Comment 20 by effigies ---
Sure. Do you know off the top of your head a dataset that reproduces the issue?

--- END ---