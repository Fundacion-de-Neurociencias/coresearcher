# MRG: New time gen class (#1629)
URL: https://github.com/mne-tools/mne-python/pull/1629
State: closed | PR: YES
Comments: 127 | Created: 2014-10-29T18:57:23Z | Closed: 2015-03-11T20:13:20Z

## Body (first 1000 chars)
Closes #1302. 

@kingjr sorry rebasing was a mess, I had to squash your commits to get started within a finite amount of time. Your commits are supposed to be logged and counted anyways

Here's a list of things I addressed.
1. Enforce sklaern API that distinguishes between parametersa and attributes
2. make score and predict return the corresponding values
3. fix unfarable expression which create references not copies e.g `[[]] * len(test_times` creates a list of len(test_times) times the same list object.
4. fix the default y and simplify the example. I figured out that sklearn apparently expects 0 and 1 or True and False for the binary case. Using scipy.stats.rankdata as a trick to achieve this.
5. isolated the changes related to the new class from the changes related to the previous attempt to modify the existing function.
6. rebased and fixed unit tests.
7. caught a corner case where predict == 'distance' will crash (binary casses).
8. addressed pep8 issues
9. added doc to better d

## Comments

--- Comment 1 by dengemann ---
@agramfort (and @kingjr) 
1. addressed comments.
2. moved plotting function in designated viz module.
3. added viz tests for decoding.

Travis should turn happy and another round of reviews is welcome.


--- Comment 2 by kingjr ---
@dengemann Great, thanks a lot that must have been a lot of work. I havent been able to run the code yet, but made some small comments. The only important thing before release would be to change the name of the var 'independent', to allow later developments. We ll discuss in details this afternoon at approx. 1630 French time. 


--- Comment 3 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/1404122/badge)](https://coveralls.io/builds/1404122)

Coverage decreased (-17.19%) when pulling **933945db1206131215218ceb0642c689fd7a23cf on dengemann:new_time_gen** into **1f4ab3d090babe2fe3be1b684cc4c04c9312e97d on mne-tools:master**.


--- Comment 4 by dengemann ---
@agramfort @kingjr here are some benchmarks. As expected the new function

![screenshot 2014-10-30 13 50 24](https://cloud.githubusercontent.com/assets/1908618/4843550/98125cca-6033-11e4-9d90-063dea23990e.png)
![screenshot 2014-10-30 13 49 40](https://cloud.githubusercontent.com/assets/1908618/4843551/9812d902-6033-11e4-8ac0-f7ab9ba35513.png)

As expected the new function consumes more memory and is a bit slower. Not sure how this scales with more realistic examples. 


--- Comment 5 by dengemann ---
Here's the comparisons for a single job.

![screenshot 2014-10-30 13 59 14](https://cloud.githubusercontent.com/assets/1908618/4843644/a7f5e2b4-6034-11e4-8b89-6384fd4c1dbb.png)
![screenshot 2014-10-30 13 58 34](https://cloud.githubusercontent.com/assets/1908618/4843645/a7fd3474-6034-11e4-9cd0-b537229e05c7.png)

here's the testing script: https://gist.github.com/dengemann/137f41efe596c320658d


--- Comment 6 by dengemann ---
Travis should now be less borderline. I fixed his pandas.


--- Comment 7 by agramfort ---
it's not a significant difference which is good


--- Comment 8 by dengemann ---
> it's not a significant difference which is good

indeed. I think we can live with it. 


--- Comment 9 by dengemann ---
Notes from a meeting with @kingjr 
1. `independent` -> `predict_mode` and allow for string
2. remove 'distance' for now
3. add more tests and see what creates low coverage, especially test combinations of slcices etc., also test for multiple classes, score ==100% if wrongly indicated independent
   (or close to 100%)
4. call `tt_times``-->``window_params``


--- Comment 10 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/1406452/badge)](https://coveralls.io/builds/1406452)

Coverage increased (+35.94%) when pulling **2f241d79fc3e39b06ad7963dc2560a555ebb410e on dengemann:new_time_gen** into **bdbdf6c90bd738ee2c4a506755db0374bb63c70f on mne-tools:master**.


--- Comment 11 by dengemann ---
@kingjr it seems coverage was actually ok.


--- Comment 12 by dengemann ---
@kingjr @agramfort @Eric89GXL I rebased. I think everything is good for now. There has been a misleading coverage report, but it seems tests are sufficient. I would be +1 for merge, but more reviews woule be even better.


--- Comment 13 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/1421072/badge)](https://coveralls.io/builds/1421072)

Coverage decreased (-0.04%) when pulling **5cc517207d012651493f760240ac7db1bd5c3b96 on dengemann:new_time_gen** into **7e5b90e8b838922c8724b26e1711dbf135b6db11 on mne-tools:master**.


--- Comment 14 by kingjr ---
@dengemann Thanks!


--- Comment 15 by agramfort ---
@kingjr please review, try with some more data and comment.


--- Comment 16 by kingjr ---
I m working on it. There s a big issue with the CV. I'll keep you posted. 


--- Comment 17 by dengemann ---
Rebased. One more iteration polishing. Thanks @kingjr for your assistance.


--- Comment 18 by dengemann ---
@agramfort with stricter filters it looks better. We should not be too much confused by the baseline. With the other sensor decoding example we also have scores sometimes closer to .6 in the basleine. At some point we should add confidence intervals or stanard deviations to the plotting. Later PRs.


--- Comment 19 by dengemann ---
@kingjr some additional comments on predict modes would be great.


--- Comment 20 by dengemann ---
multic class decoding also seems to work.

![screenshot 2014-11-11 17 34 56](https://cloud.githubusercontent.com/assets/1908618/4996783/003270ca-69ca-11e4-8a1c-e5a7d6e3a70e.png)


--- END ---