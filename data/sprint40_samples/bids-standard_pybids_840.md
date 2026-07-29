# [ENH] Update config to support microscopy, qMRI, PET, ASL (#840)
URL: https://github.com/bids-standard/pybids/pull/840
State: closed | PR: YES
Comments: 7 | Created: 2022-04-14T12:09:44Z | Closed: 2022-04-24T20:20:39Z

## Body (first 1000 chars)
closes #807 

should cover both new entities and default path patterns

most of this was done by reading from the bids schema and relying on elbow grease and patience to do the rest.

Cannot wait for #818 to be done so I never have to do this by hand ever again but in the mean time: here we go.

Has not been properly tested yet:
- path patterns

## Comments

--- Comment 1 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/bids-standard/pybids/pull/840?src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard) Report
> Merging [#840](https://codecov.io/gh/bids-standard/pybids/pull/840?src=pr&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard) (4c5e504) into [master](https://codecov.io/gh/bids-standard/pybids/commit/c81e7f90180ce813c1100269ab2eba89fa202865?el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=bids-standard) (c81e7f9) will **increase** coverage by `0.17%`.
> The diff coverage is `n/a`.

> :exclamation: Current head 4c5e504 differs from pull request most recent head 669200a. Consider uploading reports for the commit 669200a to get more accurate results

```diff
@@            Coverage Diff             @@
##           master     #840      +/-   ##
==========================================
+ 

--- Comment 2 by Remi-Gau ---
Removed this pattern that caused a test to fail:

```
"[acq-{acquisition}]_photo{extension<json>|json}"
```

Apparently from the comment in the test and the related PR, this test was put there to caught patterns that are too general.

https://github.com/bids-standard/pybids/pull/574#discussion_r366447600

--- Comment 3 by effigies ---
@Remi-Gau the error is related to dropping a new data directory into the Python source tree.

I would suggest instead of doing this, that we create a git submodule in the project root, look for it in `conftest` and make it available as a fixture. Is that all clear, or would you like me to give it a shot in a separate PR?

--- Comment 4 by Remi-Gau ---
> @Remi-Gau the error is related to dropping a new data directory into the Python source tree.

oh that's the pythonic way to say this? Noted. :-p


> I would suggest instead of doing this, that we create a git submodule in the project root, look for it in `conftest` and make it available as a fixture. Is that all clear, or would you like me to give it a shot in a separate PR?

mostly clear but let's chat about all this tomorrow during our bids maintainers meeting because I have other questions about this PR that could benefit from a video call. 

--- Comment 5 by Remi-Gau ---
for the record here is an example of what I get for  "micr_SPIM"

```python
ds = join(get_test_data_path(), "bids-examples", "micr_SPIM")
layout = BIDSLayout(ds)
files = layout.get(return_type="file")
print(files)

['/home/remi/github/pybids/bids/tests/data/bids-examples/micr_SPIM/dataset_description.json', 
'/home/remi/github/pybids/bids/tests/data/bids-examples/micr_SPIM/participants.json', 
'/home/remi/github/pybids/bids/tests/data/bids-examples/micr_SPIM/participants.tsv', 
'/home/remi/github/pybids/bids/tests/data/bids-examples/micr_SPIM/README']
```

--- Comment 6 by Remi-Gau ---
> I was wondering if it would be possible to add the `samples.tsv` file to the `get_collections `function at the "dataset" level At the moment, the "dataset" level seems to only index metadata from `participants.tsv`.
> 
> For example on `micr_SPIM` with:
> 
> ```
> subj_df = layout.get_collections(level='dataset', merge=True).to_df()
> subj_df
> ```
> 
> I get the following from `participant.tsv`, but `samples.tsv` metadata is not present: ![image](https://user-images.githubusercontent.com/54086142/164043261-7c209809-a37c-4109-8c92-5ce5f051c572.png)

I suggest moving this to a different issue and fix it in a different PR


--- Comment 7 by Remi-Gau ---
This is good for a final review for me.

Tests are still failing locally but that's a me problem.

--- END ---