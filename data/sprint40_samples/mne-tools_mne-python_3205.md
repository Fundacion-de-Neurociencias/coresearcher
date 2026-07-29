# MRG+1: Elekta averager  (#3205)
URL: https://github.com/mne-tools/mne-python/pull/3205
State: closed | PR: YES
Comments: 164 | Created: 2016-05-03T13:18:42Z | Closed: 2016-09-24T20:05:33Z

## Body (first 1000 chars)
Discussed in #3097 

Summary: Elekta/Neuromag DACQ (data acquisition) supports rather flexible event and 
averaging logic that is currently not implemented in mne-python. It also stores all averaging 
parameters in the fiff file, so raw data can be easily reaveraged in postprocessing.
The purpose of this PR is 
1) extract the relevant info from the fiff file 
2) implement support for averaging according to DACQ categories (or to modify the categories first)

Implementation: a class that takes all the relevant info from `raw.info['acq_pars']`.

API:
get_condition() gives averaging info for a given condition, that can be fed to mne.Epochs

Technical details: DACQ supports defining 32 different events which correspond to trigger 
transitions. Events support pre- and post-transition bit masking. Based on the events, 32 averaging categories can be defined. Each category defines a reference event that is the zero-time point for collecting the corresponding epochs. Epoch length is defined by 

## Comments

--- Comment 1 by agramfort ---
can you run flake8 tool on your code and follow the pep8 guidelines?
you could put the code in an elekta_events.py file for now.


--- Comment 2 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/6045705/badge)](https://coveralls.io/builds/6045705)

Coverage decreased (-0.2%) to 90.651% when pulling **e9a5353fb89daacc897e06ba7880ce91e0c83307 on jjnurminen:elekta_avg** into **f932004db951abaf7d0522f961ca9a3be6e72167 on mne-tools:master**.


--- Comment 3 by jjnurminen ---
I dug a little into the TRIUX/Vectorview issue.
In my current understanding, the code is already compatible with both TRIUX and Vectorview data, as long as it was measured with DACQ version => 3.4 (released in 2005). According to the fiff info, the `sample_audvis_raw.fif` example data was measured in 2002, so it's pretty old. For testing the averager, I would definitely like to use newer data.
I can try to implement support for DACQ < 3.4 if I can get the specs from Elekta, but I'm not sure how many people will actually be processing such ancient files. ;)


--- Comment 4 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/6098298/badge)](https://coveralls.io/builds/6098298)

Coverage decreased (-10.8%) to 79.988% when pulling **77fa95ec06950e0c366eddbbf2f64d74bcb5c0f9 on jjnurminen:elekta_avg** into **f932004db951abaf7d0522f961ca9a3be6e72167 on mne-tools:master**.


--- Comment 5 by jjnurminen ---
I created a fiff file (95 megs) with various event/category definitions and some environmental interference acting as "signal". With that file, the code above now seems to give results identical to the MaxFilter averager (except for some baseline effect, haven't yet figured out where it comes from). I guess this fiff could be used for the unit tests eventually.


--- Comment 6 by coveralls ---
[![Coverage Status](https://coveralls.io/builds/6101712/badge)](https://coveralls.io/builds/6101712)

Coverage decreased (-0.1%) to 90.694% when pulling **31e24941edc42c5281705fef23cb0b2adb59794b on jjnurminen:elekta_avg** into **f932004db951abaf7d0522f961ca9a3be6e72167 on mne-tools:master**.


--- Comment 7 by larsoner ---
>  I guess this fiff could be used for the unit tests eventually.

Sure. Maybe to keep file size down you could do `raw.pick_channels(...)` and pick a few MEG channels, plus the STI channel(s) you need. That plus the `-ave.fif` from Elekta's program would make for a good set of unit tests.


--- Comment 8 by jjnurminen ---
I still get a DC shift compared to the Elekta averager, so my unit tests don't pass at the moment. I'm waiting for response from Elekta to confirm that their code really doesn't do any baseline or filtering operations.


--- Comment 9 by larsoner ---
Have you tried putting in a baseline to see if it gets closer? You could also compute the PSD of the two datasets to get some evidence of whether or not filtering has been applied


--- Comment 10 by jjnurminen ---
@Eric89GXL If I apply a pre-stimulus baseline to the epochs before averaging, I get almost 100% match with Elekta data, but Elekta claims that they don't use any baseline in their averager. 

BTW, do you know why the audvis_raw example data does not have info['acq_pars'] at all? I guess it was somehow modified and rewritten? My goal would be to implement support also for pre-3.4 DACQ versions (older Vectorview systems), so I guess more testing data would be needed for that. I can try to find some old data from our lab.


--- Comment 11 by larsoner ---
> I get almost 100% match with Elekta data, but Elekta claims that they don't use any baseline in their averager.

Our precedent in cases like this is to put some indignant comment like "# XXX this baseline is necessary to get a good match even though the Elekta averager isn't supposed to baseline correct???" and do what is necessary to get a good match :) That  way it won't hold up the PR while we wait for clarification.

The sample data are old, and from MGH. Maybe they have a special setup...? I don't think anyone manually removed it. The best thing is probably to find data from your lab.


--- Comment 12 by jjnurminen ---
OK. Just to be sure, can you confirm my understanding that the following sequence of operations should perform no baselining, detrending or filtering whatsoever:
1. raw = mne.io.raw(filename)
2. eps = mne.Epochs(raw [...], baseline=None, detrend=None)
3. avs = eps.average()


--- Comment 13 by larsoner ---
Yep, that should do it. You can confirm by doing `avs.plot()`, you'll see the butterfly plot drifts


--- Comment 14 by jjnurminen ---
Yep. The funny thing is that the MaxAve data is also shifted, but by a different amount. Applying baseline to both makes them identical. Anyway, evoked responses are usually baselined before analysis, so I guess it's not a big deal. I'll just write the unit tests for the baselined data as you suggested.


--- Comment 15 by larsoner ---
Don't forget the angry/confused comment, too :) But seriously put in a comment with `XXX` in it somewhere, it's often how we flag things that are mysterious and can hopefully be fixed later


--- Comment 16 by jjnurminen ---
Will do.


--- Comment 17 by jjnurminen ---
There's now an unit test that averages all categories from the raw data and compares to Elekta averaged data to within 1 fT(/cm). I truncated the raw file to 3 MEG channels.


--- Comment 18 by larsoner ---
Can you open a PR to add the data file to the mne-testing-data repository? 


--- Comment 19 by larsoner ---
I guess you'll probably add a raw and an evoked file? 


--- Comment 20 by jjnurminen ---
Sure, but I'm a bit confused about where the files should go? The test files under mne/io/tests/data/ don't seem to be in the mne-testing-data repository.


--- END ---