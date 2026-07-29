# REFACTOR: 0.8 [WIP] (#369)
URL: https://github.com/bids-standard/pybids/pull/369
State: closed | PR: YES
Comments: 36 | Created: 2019-01-29T23:56:16Z | Closed: 2019-02-15T18:44:50Z

## Body (first 1000 chars)
This is a near-total refactoring of the core `BIDSLayout` object. The main point of this exercise is to increase maintainability (I don't want to be in charge of this forever) by removing the grabbit dependency and increasing code clarity. With a few very minor exceptions, the user-facing API remains unperturbed (as evidence of that, the tests for most modules passed with virtually no modification). Two side benefits of the overhaul are that (a) indexing should be substantially more efficient, and (b) there's a new (currently undocumented) object-oriented API that allows one to walk down a BIDS project (each `BIDSLayout` has a `root_node` attribute, which is a `BIDSNode` object that has helpful attributes like `.children`, `.parent`, `.path`, `entities`, etc.).

**API changes**:
I believe the only common case where this PR breaks the public 0.7 API is in the handling of derivatives in `get()` calls. Previously, `get` took a `derivatives` argument that indicates whether to search der

## Comments (first 1000 chars each)

--- Comment 1 by effigies ---
Ah, sorry. Bad moment to merge #357. At least one of those conflicts is from there. Feel free to revert.

--- Comment 2 by tyarkoni ---
No worries, it'll probably still be at least a week or two before this is ready to go. I think it's fine to keep updating master in the meantime; I'll make a pass through any new PRs before finalizing this one.

--- Comment 3 by yarikoptic ---
what is the advantage of cutting the umbilical cord from grabbit if you are to port big portion (majority?) of it into pybids?  The original description here provides only an abstract motivation (maintainability).  Although I see how keeping all functionality in a more targeted pybids might be beneficial, I am afraid that if you are still to keep grabbit alive, you might end up then porting/duplicating bug fixes between the two instead of solving them in a single location (grabbit), which would be actually counter productive.

--- Comment 4 by tyarkoni ---
I don't plan to maintain grabbit independently, beyond critical bugfixes. And this isn't really a port of the grabbit code so much as a port of its functionality. The public API is the same, but most of the internals are totally different (and much simpler).

--- Comment 5 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/369?src=pr&el=h1) Report
> Merging [#369](https://codecov.io/gh/bids-standard/pybids/pull/369?src=pr&el=desc) into [master](https://codecov.io/gh/bids-standard/pybids/commit/e9fc2df43d560b75190f4e4cb6300f8ba5442a2b?src=pr&el=desc) will **decrease** coverage by `12.62%`.
> The diff coverage is `68.66%`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/369/graphs/tree.svg?width=650&token=0d39OR1fhx&height=150&src=pr)](https://codecov.io/gh/bids-standard/pybids/pull/369?src=pr&el=tree)

```diff
@@             Coverage Diff             @@
##           master     #369       +/-   ##
===========================================
- Coverage   73.27%   60.64%   -12.63%     
===========================================
  Files          24       27        +3     
  Lines        2604     4485     +1881     
  Branches      640     1137      +497     
===========================================
+ Hits         190

--- Comment 6 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/369?src=pr&el=h1) Report
> Merging [#369](https://codecov.io/gh/bids-standard/pybids/pull/369?src=pr&el=desc) into [master](https://codecov.io/gh/bids-standard/pybids/commit/6e857b46c9c4adfa7ca13a08c641a5b675092608?src=pr&el=desc) will **decrease** coverage by `11.44%`.
> The diff coverage is `74.65%`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/369/graphs/tree.svg?width=650&token=0d39OR1fhx&height=150&src=pr)](https://codecov.io/gh/bids-standard/pybids/pull/369?src=pr&el=tree)

```diff
@@             Coverage Diff             @@
##           master     #369       +/-   ##
===========================================
- Coverage   73.78%   62.33%   -11.45%     
===========================================
  Files          23       27        +4     
  Lines        2491     4559     +2068     
  Branches      621     1175      +554     
===========================================
+ Hits         183

--- Comment 7 by tyarkoni ---
Question: is anyone currently using the `load_index` and `save_index` functionality in pybids? @yarikoptic and @mih, I think you had talked about this at some point; is datalad actually making use of this?

I ask because if nobody's using the existing functionality (and I doubt anybody outside the core devs is), I'm tempted to drop it from 0.8 and add a more comprehensive serialization solution later on. The current approach is kind of half-assed and doesn't seem terribly useful.

--- Comment 8 by effigies ---
I'm not, but I was considering it if I ever needed to avoid building a layout in two separate nipype nodes.

--- Comment 9 by tyarkoni ---
I definitely plan to add serialization options again, and we can raise the priority if you need it. I just want to make sure no one's currently relying on the existing API, because I would rather break it and do something more sensible.

--- Comment 10 by yarikoptic ---
According to https://github.com/datalad/datalad-neuroimaging/search?q=load_index&unscoped_q=load_index we don't use it ATM

--- Comment 11 by tyarkoni ---
Alright, I'm going to leave it out of the port then, and will revisit serialization/export more systematically later.

--- Comment 12 by tyarkoni ---
Okay, I think we're good to go on this, pending the outcome of #378 and any associated patch. I have *not* ported all the tests over from grabbit yet, but I'm hesitant to wait any longer on that, because (a) it will make reconciliation with 0.7.1 more difficult the longer we wait, and (b) the vast majority of functionality that used to live in grabbit is implicitly covered by the existing tests, or new ones I've added (e.g., between all the BIDSLayout-specific tests of `get`, most of the old `get` options in grabbit are already covered).

--- Comment 13 by tyarkoni ---
@adelavega I implemented `exclude` and `force_index` arguments as described above. You can now still pass a regex, but it has to be a compiled `SRE_Pattern`, and can't be an ordinary string. When you have a chance, can you verify this branch works for you? You can wait till I merge master in if you prefer—that may take a while, depending on how bad the conflict situation is.

--- Comment 14 by tyarkoni ---
Okay, I think this is basically ready for review—it's current with master as of about half an hour ago. Not sure if anyone wants to dig through the extensive changes in detail, but at minimum let's see if this works with fitlins (paging @effigies and @delavega). There will probably be some minor changes to code required, as parts of the API have changed, but shouldn't be anything approaching 0.7 levels. I'll work on a changelog update.

--- Comment 15 by adelavega ---
Aside from changing one instance of `_get_nearest_helper` it worked great on neuroscout backend's tests (which cover a decent range of uses).

I'll test next on `neuroscout-cli` 

--- Comment 16 by adelavega ---
@effigies When I pass `--exclude` to fitlins, can that get compiled as a regex to be passed on to `pybids`. If so then I believe it should work. 

--- Comment 17 by adelavega ---
Do you have a branch you're working on with changes? fitlins is failing for me because if `include`


--- Comment 18 by effigies ---
Oh, let me push.

--- Comment 19 by effigies ---
https://github.com/poldracklab/fitlins/compare/master...effigies:pin/pybids_0.8

--- Comment 20 by effigies ---
The include/exclude stuff is your playground, AFAIC. You can do whatever you like with it.

--- END ---