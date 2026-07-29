# MRG+4: Epochs metadata (#4414)
URL: https://github.com/mne-tools/mne-python/pull/4414
State: closed | PR: YES
Comments: 209 | Created: 2017-07-21T19:07:03Z | Closed: 2017-10-19T18:30:48Z

## Body (first 1000 chars)
This is a rough draft of the metadata attribute for the `Epochs` object. The code is mostly there, and I put together a tutorial + some tests that still need tweaking. Let's see what the rendered circle output looks like and then decide whether we like it or not :-)

The main thing this does is:

* Lets you add a `metadata` attribute to `Epochs` objects. This is a dataframe that can be stored w/ the object.
* Lets you do pandas query-style things with the `__getattr__` method in Epochs. (see example)

# Todo
- [x] Add I/O stuff
- [x] tutorial

ping @agramfort @Eric89GXL @jona-sassenhagen @kingjr 

# Follow-up PRs
* Deal with `groupby` functionality for making `Evoked` (or `Epochs`?) instances

## Comments (first 1000 chars each)

--- Comment 1 by choldgraf ---
Aaand I broke the epochs tests. OK so I think this probably a problem w/ the logic that happens when you call `__getitem__` with epochs.

How should we handle this? Essentially the question is "how does epochs know when a string input corresponds to a pandas query, vs. when it corresponds to a 'current behavior' field"?

--- Comment 2 by larsoner ---
> How should we handle this? Essentially the question is "how does epochs know when a string input corresponds to a pandas query, vs. when it corresponds to a 'current behavior' field"?

You could try the string behavior, if it fails, fall back to Pandas, if it fails, throw error. Tell people not to have their Pandas entries and `event_ids` overlap.

--- Comment 3 by choldgraf ---
So right now I'm doing the opposite I think :-) 

basically:

1. see if pandas is installed, if so:
  1. Try running the string as a query
  2. If that succeeds then proceed, if that fails then try:
2. Running the string as the current string behavior
3. If that fails, then error

Though I agree I think it should be the other way around...lemme try that

--- Comment 4 by jona-sassenhagen ---
I haven't thought about it in too much detail. Just one suggestion: would there be a way to more directly integrate it with "/"-matching?

--- Comment 5 by agramfort ---
I have the feeling that this will require some community discussion :)

shall we keep this for the next sprint early 2018? this PR is already a big step forward.


--- Comment 6 by larsoner ---
> I have the feeling that this will require some community discussion :)

It seems like if we remove the `regress` function, then we have already converged, no?

--- Comment 7 by agramfort ---
ok then :) let's remove regress and find a good dataset we can host to demo this !

--- Comment 8 by choldgraf ---
+1 

I'll just change the module name to NeuroPandas and we can merge.

--- Comment 9 by agramfort ---
+np.finfo['float128'].max :)


--- Comment 10 by choldgraf ---
haha - I will try to get to another iteration on this over the weekend or next week...in the meantime I had to deal with a last-second berkeley bureaucracy graduation crisis :-)

--- Comment 11 by dengemann ---
Yes let's indeed discuss face to face. Also -1 on regress method now. If
you want to experiment make an example that exposes the functionality in
the sense of a demo / pre-API idea.
On Sat, 29 Jul 2017 at 02:54, Chris Holdgraf <notifications@github.com>
wrote:

> haha - I will try to get to another iteration on this over the weekend or
> next week...in the meantime I had to deal with a last-second berkeley
> bureaucracy graduation crisis :-)
>
> —
> You are receiving this because you are subscribed to this thread.
> Reply to this email directly, view it on GitHub
> <https://github.com/mne-tools/mne-python/pull/4414#issuecomment-318792050>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/AB0fikRt8mswEPgC4FqHa1u1gyBj-SE5ks5sSoLVgaJpZM4Ofx-h>
> .
>


--- Comment 12 by choldgraf ---
so @Eric89GXL , what's the way to handle I/O here? I don't have a ton of experience with the elektra binary files...

--- Comment 13 by larsoner ---
From @agramfort on Gitter:

> I would create a new FIFFB_EPOCHS_METADATA block. We need to store the columns as list of strings and then arrays on int, float or str

So we need to add a new constant to `mne.io.constants.FIFF` for this new block. Then based on what @agramfort wrote, if you look at the existing Epochs I/O I think it will already make sense to you. There are pretty simple functions to open/close the new block, and write/read chunks / tags of data as necessary.

One thing I'm not sure about is how we're going to store the column header names. Currently in MNE we turn a list of strings into a colon-separated single string for writing (`*_name_list`). @agramfort do we require no `:` in the header titles, or do some sanitizing during I/O? (@choldgraf you can proceed with trying to implement the solution before this question is answered.)

--- Comment 14 by agramfort ---
yes we use : so far. It's maybe not super robust. I take suggestions


--- Comment 15 by choldgraf ---
would it break things if we used JSON?

```
In [16]: data.to_json()
Out[16]: '{"a":{"0":1,"1":3},"b":{"0":2,"1":4}}'

In [17]: pd.read_json(data.to_json())
Out[17]:
   a  b
0  1  2
1  3  4
```

--- Comment 16 by dengemann ---
It should work, I think we used it for serialization in ICA -> fif. Worth a
try. I remember there were some annoying corner cases though. Not
everything could be nicely serialized.

On Mon, Jul 31, 2017 at 6:01 PM Chris Holdgraf <notifications@github.com>
wrote:

> would it break things if we used JSON?
>
> In [16]: data.to_json()
> Out[16]: '{"a":{"0":1,"1":3},"b":{"0":2,"1":4}}'
>
> In [17]: pd.read_json(data.to_json())
> Out[17]:
>    a  b
> 0  1  2
> 1  3  4
>
> —
> You are receiving this because you commented.
>
>
> Reply to this email directly, view it on GitHub
> <https://github.com/mne-tools/mne-python/pull/4414#issuecomment-319114980>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/AB0fijIssuyTlzBfx6GllD45iwAKeJhVks5sTfppgaJpZM4Ofx-h>
> .
>


--- Comment 17 by larsoner ---
This will probably become inefficient for binary data (e.g., float), not
sure if it would matter.

If we do this string dump we can just use FIFF_DESCRIPTION string field,
and thus avoid a new constant


--- Comment 18 by choldgraf ---
so it seems like the event IDs are stored like this:

```
mapping_ = ';'.join([k + ':' + str(v) for k, v in
                         epochs.event_id.items()])
```

does that mean that I could just store the metadata by doing

`mapping_ += ';EVENT_METADATA: %s' % self.metadata.to_json()`

?

--- Comment 19 by dengemann ---
I can imagine scenarios where this will get inefficient. What about going
column wise and depending on dtype use fiff functions to write float/int
matrix, if string then serialize.
On Mon, 31 Jul 2017 at 19:26, Chris Holdgraf <notifications@github.com>
wrote:

> so it seems like the event IDs are stored like this:
>
> mapping_ = ';'.join([k + ':' + str(v) for k, v in
>                          epochs.event_id.items()])
>
> does that mean that I could just store the metadata by doing mapping_ +=
> ';EVENT_METADATA: %s' % self.metadata.to_json()?
>
> —
> You are receiving this because you commented.
>
>
> Reply to this email directly, view it on GitHub
> <https://github.com/mne-tools/mne-python/pull/4414#issuecomment-319136231>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/AB0fitUHNcDPBc_nD3hgnQFLlhbJ_eSGks5sTg5DgaJpZM4Ofx-h>
> .
>


--- Comment 20 by dengemann ---
Another option would be to see if columns can be grouped by type. Then you
could store blocks of same dtype and save an index / column names
separately for reading.
On Mon, 31 Jul 2017 at 19:36, Denis-Alexander Engemann <
denis.engemann@gmail.com> wrote:

> I can imagine scenarios where this will get inefficient. What about going
> column wise and depending on dtype use fiff functions to write float/int
> matrix, if string then serialize.
> On Mon, 31 Jul 2017 at 19:26, Chris Holdgraf <notifications@github.com>
> wrote:
>
>> so it seems like the event IDs are stored like this:
>>
>> mapping_ = ';'.join([k + ':' + str(v) for k, v in
>>                          epochs.event_id.items()])
>>
>> does that mean that I could just store the metadata by doing mapping_ +=
>> ';EVENT_METADATA: %s' % self.metadata.to_json()?
>>
>> —
>> You are receiving this because you commented.
>>
>>
>> Reply to this email directly, view it on GitHub
>> <https://github.com/mne-tools/mne-python/pull/4414#issueco

--- END ---