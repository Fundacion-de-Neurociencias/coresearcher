# MAINT: Add .zenodo.json (#308)
URL: https://github.com/bids-standard/pybids/pull/308
State: closed | PR: YES
Comments: 11 | Created: 2018-11-28T18:59:55Z | Closed: 2018-12-12T14:03:26Z

## Body (first 1000 chars)
Todo:

* [x] "Last, First M." format for names
* [ ] Get all affiliations, ORCIDs, preferred spellings
* [x] Add additional .zenodo fields

Closes #299.

## Comments

--- Comment 1 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/308?src=pr&el=h1) Report
> Merging [#308](https://codecov.io/gh/bids-standard/pybids/pull/308?src=pr&el=desc) into [master](https://codecov.io/gh/bids-standard/pybids/commit/fd9ac089707a674b9e5cd021e4c2931211f077b8?src=pr&el=desc) will **decrease** coverage by `0.18%`.
> The diff coverage is `n/a`.

[![Impacted file tree graph](https://codecov.io/gh/bids-standard/pybids/pull/308/graphs/tree.svg?width=650&token=0d39OR1fhx&height=150&src=pr)](https://codecov.io/gh/bids-standard/pybids/pull/308?src=pr&el=tree)

```diff
@@            Coverage Diff             @@
##           master     #308      +/-   ##
==========================================
- Coverage   73.03%   72.84%   -0.19%     
==========================================
  Files          24       24              
  Lines        2551     2563      +12     
  Branches      624      630       +6     
==========================================
+ Hits         1863     1867   

--- Comment 2 by tyarkoni ---
It just occurred to me that we should probably include folks who contributed to grabbit but not pybids. Is it feasible to integrate the grabbit contributor list, or should we add those folks manually? Sorry, I should have thought of this earlier...

--- Comment 3 by effigies ---
Yeah, we can add them. Probably makes the most sense to run from the latest tag?

--- Comment 4 by yarikoptic ---
Just want to thank you @effigies for doing this so meticulously!

--- Comment 5 by choldgraf ---
Hey all - I'd like to cite this in the BIDS-iEEG preprint...any timeline on when this PR will land?

--- Comment 6 by effigies ---
@choldgraf This PR can land pretty much any time (though there are some non-responses, which means I might need to remove affiliations I'm not positive of), but the bigger problem is that we're not sure when the next release will hit.

@tyarkoni @adelavega Thoughts? If we cut 0.7.0 this week, I think we'd have to be ready for a lot of bug reports and 0.7.1 next week.

--- Comment 7 by choldgraf ---
Cool - well FWIW we'll submit the psyrxiv version on Thursday most likely, so I'll cite the DOI or the URL of this repo depending on whether the DOI exists or not!

--- Comment 8 by effigies ---
Okay. Well I think this is mergeable. @tyarkoni Care to review?

We're missing confirmations/corrections from the following:

* @lodurality
* @hyperswitcher 
* @mih 
* @oesteban 
* @jbpoline 
* ~~@poldrack~~
* @bthirion 
* @PaulineRoca

I am reasonably confident that they all at least at one time held the affiliations I've filled in for them. The main other thing to check is whether we want to add other metadata.

--- Comment 9 by tyarkoni ---
LGTM, though I didn't go through the `prep_zenodo.py` script in detail (and don't feel a need to).

Assuming that Zenodo generates a new version for every release, I don't think it matters much when the next release happens. If one or two people's info is wrong for a few weeks/months, we can live with that.

Thanks!

--- Comment 10 by effigies ---
tools/prep_zenodo.py should be run and any changes inspected and committed before a release.

--- Comment 11 by choldgraf ---
does anybody know how to import a zenodo ref from a github repo into zotero?

--- END ---