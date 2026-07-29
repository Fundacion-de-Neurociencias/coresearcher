# WIP/ENH: add repeated measures twoway anova function (#580)
URL: https://github.com/mne-tools/mne-python/pull/580
State: closed | PR: YES
Comments: 151 | Created: 2013-04-26T21:19:52Z | Closed: 2013-05-14T00:12:29Z

## Body (first 1000 chars)
This addresses #226 and some aspects of #535

Adapted from my gist: 
https://gist.github.com/dengemann/5427106

which is a translation of MATLAB code by Rik Henson:
http://www.mrc-cbu.cam.ac.uk/people/rik.henson/personal/repanova.m

and to some lesser extend by Python code from pvttbl by Roger Lew.
http://code.google.com/p/pyvttbl/

While there is a new WIP PR in statsmodels related to this (https://github.com/statsmodels/statsmodels/pull/786), this minimal version aims at supporting our (mass-univariate) use case.

Some features:
- supports joblib (on my 2011 macbook air it took me 7 minutes to
  compute 1.000.000 repeated measures anovas for 18 subjects and
  all three effects from a 2 x 2 design using 2 jobs). I might find a more efficient way to do this, but I think this is definitely start.
- supports sphericity correction for factor levels > 2

Current limitations are:
- to keep things simple, I constrained this function to only estimate models with 2 factors. This should make se

## Comments

--- Comment 1 by larsoner ---
I have been using some code of a collaborator that uses a two-way ANOVA with time as one of the "ways" to gain statistical power... I should be able to compare these two bits of code at some point. I'm happy to send the snippet to you if you'd like to :)


--- Comment 2 by dengemann ---
> I'm happy to send the snippet to you if you'd like to :) 

Sure! Times should also work this this. The second factor may have multiple levels.


--- Comment 3 by larsoner ---
See if this makes sense to you:

https://gist.github.com/Eric89GXL/1d59fc1085c0a4798318


--- Comment 4 by dengemann ---
Looks cool, but also looks like a slightly different approach / use case. I'd be happy to add it though. Maybe don't mix it with this PR? Unless you immediately see how to get all this done in one function ;-)


--- Comment 5 by larsoner ---
I'm wondering if the approaches can be made equivalent somewhere... maybe I'll try using your code to see if I can get similar results.


--- Comment 6 by dengemann ---
Her some minimum example:

``` Python
import numpy as np
from mne.stats.parametric import r_anova_twoway

data = np.random.random([18, 4, 100])
print r_anova_twoway(data, [2, 2], n_jobs=2)
```

I think the idea of this one is slightly different. This one is a brute force mass univariate function that just goes through which ever chain of nsubj X condition matrices to compute interactions. But maybe we can combine it somehow, even if its just about the computation.
If you're happy to wait I'll soon add a TFR example for a 2x2 interaction image.


--- Comment 7 by larsoner ---
The example should be helpful. So long as the function returns F values for each condition / interaction, we should be able to make them equal. I'll see what I can get.


--- Comment 8 by dengemann ---
> The example should be helpful.

Yes, it's coming.

> So long as the function returns F values for each condition / interaction, we should be able to make them equal.

Yes, as it is in the moment it returns 3 F values for A, B, A:B for each of the observations (last dimension) 


--- Comment 9 by larsoner ---
@dengemann if I use your example but change `data = np.random.random([18, 6, 100])` and `r_anova_twoway(data, [2, 3])` I get an error about matrices not being aligned. Am I being stupid with the input arguments? There should be a test for making sure the user doesn't do anything dumb with the condition counts.


--- Comment 10 by dengemann ---
> @dengemann if I use your example but change data = np.random.random([18, 6, 100]) and r_anova_twoway(data, [2, > 3]) I get an error about matrices not being aligned. Am I being stupid with the input arguments?

certainly not.

> There should be a test for making sure the user doesn't do anything dumb with the condition counts.

yes, there's supposed to be a bug, the code from my gist is quite freshly refactored. Time for writing tests :-)


--- Comment 11 by dengemann ---
... the count certainly will not support anything above 2 x 2. I'll have to revisit that more carefully. This was the result of trying to get rid of a weird binary counter function together with the iterator was producing the correct indices in the original code.


--- Comment 12 by larsoner ---
Alright, let me know when the second factor (or first factor) supports multiple levels beyond 2, and I'll see how the two methods compare.


--- Comment 13 by dengemann ---
@Eric89GXL this should now be safe enough to play with. Test added (passes) and coding bug fixed.


--- Comment 14 by larsoner ---
Okay, I'll take a look and also update my gist...


--- Comment 15 by dengemann ---
Damn it, wrong tab ... deleted my post.
But here we go: Cool. But beware of sphericity correction. That part is still buggy.


--- Comment 16 by dengemann ---
@Eric89GXL at least formally GG works. No tests at value levels so far.


--- Comment 17 by larsoner ---
Comparison Gist updated, gotta run now...


--- Comment 18 by dengemann ---
Cool, looks like the next thing to checkout. Something seems wrong with the meshgrid call ...


--- Comment 19 by dengemann ---
... ok, I'm using an older numpy version ...


--- Comment 20 by dengemann ---
So, here we go with a new repeated measures example that detects a potential interaction between stimulation modality and location in the beta band.


--- END ---