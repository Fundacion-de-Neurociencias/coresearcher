# MRG+2: add rERP/rERF (#2304)
URL: https://github.com/mne-tools/mne-python/pull/2304
State: closed | PR: YES
Comments: 91 | Created: 2015-07-15T14:24:09Z | Closed: 2015-07-23T07:33:51Z

## Body (first 1000 chars)
rERP function.
~~Missing tests.~~

Name not optimal; the original routine is of course called rERP, but @agramfort wants a name that includes MEG

See http://vorpus.org/papers/smith-kutas-2015-rerps-2-with-si.pdf

Addresses #1808

@choldgraf @wmvanvliet @teonlamont 


## Comments

--- Comment 1 by dengemann ---
Looks already pretty clean! Looking forward to seeing examples and tests.


--- Comment 2 by jona-sassenhagen ---
Example gist
http://nbviewer.ipython.org/gist/jona-sassenhagen/c43f55de773ba111111f


--- Comment 3 by dengemann ---
> Example gist

I like it, maybe we could add your data and make it downloadable.


--- Comment 4 by agramfort ---
as discussed top priority is to add tests + a cool example.


--- Comment 5 by teonbrooks ---
maybe i am missing something but why are using `raw` instead of `epochs`?


--- Comment 6 by agramfort ---
because of overlap problem between epochs. It's been a 30mins conversation
with Jona :)


--- Comment 7 by jona-sassenhagen ---
How about this for a first example @agramfort  http://nbviewer.ipython.org/gist/jona-sassenhagen/8bd1cbbb0ee5b5780410

I'm having problems with the main sample data though, see gitter


--- Comment 8 by agramfort ---
looks good. Would be nicer with more adapted data ;)


--- Comment 9 by dengemann ---
It was a problem with raw.first_samp, we just figured it out -- works
nicely on sample data.

2015-07-16 10:11 GMT+02:00 Alexandre Gramfort notifications@github.com:

> looks good. Would be nicer with more adapted data ;)
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/mne-tools/mne-python/pull/2304#issuecomment-121872465
> .


--- Comment 10 by jona-sassenhagen ---
If Travis is happy, please review for merge. Otherwise, I will fix once I'm back in Germany.

@agramfort @dengemann I will ask about permission for the gist example.


--- Comment 11 by agramfort ---
let's call it linear_regression_raw

I'll review later today

thanks heaps for tackling this !


--- Comment 12 by jona-sassenhagen ---
Tests pass, please review!


--- Comment 13 by kingjr ---
That s very nice. I have two questions for a future PR: will it be easy to pass time freq signals to this function? And will it be possible to have robust regressor (e.g. spearman) in the future ?


--- Comment 14 by agramfort ---
> That s very nice. I have two questions for a future PR: will it be easy to
> pass time freq signals to this function? And will it be possible to have
> robust regressor (e.g. spearman) in the future ?
> 
> sounds like a paper idea :)


--- Comment 15 by choldgraf ---
Hey guys - random question since I haven't chimed in on this. @jona-sassenhagen and I chatted about the code a bit, and one question I had was regularization. It seems that right now we're using a LSS for the coefficients (X^T*X)^-1 (X^T \* y).

In the regression work that I've done, I found that regularizing often resulted in a much improved model fit on held-out data (depending on the amount of data and the SNR). This seems to be especially true if you include lots of correlated covariates in the design matrix (e.g., in my case I'm including a spectrogram w/ time lags). 

I'm just wondering what you guys think about this. I think that the LSS is still very useful but perhaps it would yield better results if people were allowed to regularize? Alternatively (I hesitate to say this because it'd probably be a lot of work) in the future one could implement a more "plug n' play" approach with sklearn regression estimators, much in the same way that the TimeGen stuff works.

Just a thought!

--- Comment 16 by dengemann ---
Hi folks, keep in mind that regularization breaks linearity.
The resulting coefficients cannot be used for source localization.

On Fri, Jul 17, 2015 at 10:35 AM, Chris Holdgraf notifications@github.com
wrote:

> Hey guys - random question since I haven't chimed in on this.
> @jona-sassenhagen https://github.com/jona-sassenhagen and I chatted
> about the code a bit, and one question I had was regularization. It seems
> that right now we're using a LSS for the coefficients (X^T*X)^-1 (X^T \* y).
> 
> In the regression work that I've done, I found that regularizing often
> resulted in a much improved model fit on held-out data (depending on the
> amount of data and the SNR). This seems to be especially true if you
> include lots of correlated covariates in the design matrix (e.g., in my
> case I'm including a spectrogram w/ time lags).
> 
> I'm just wondering what you guys think about this. I think that the LSS is
> still very useful but perhaps it would yield better results if people we

--- Comment 17 by choldgraf ---
ya, I should note that I've only ever done this with ECoG, so there are likely to be important differences


--- Comment 18 by agramfort ---
my concern is not breaking linearity (as actually the estimation is still
linear). It's more that you apply this in a setup with a big tall matrix
which should be well conditionned. To support more advanced estimators then
the API should be changed to support sklearn estimators.


--- Comment 19 by dengemann ---
We just discussed with Alex and came to the conclusion that computing a
source estimate on ERP/Fs computed with regularized regresison should still
be valid but you should mnot compute classical statistics on it, such as
t-statistics that you would compute with a standard GLM. Once you
regularize you move from an estimation to a precition regime (cross
validation, etc.).

On Fri, Jul 17, 2015 at 11:07 AM, Alexandre Gramfort <
notifications@github.com> wrote:

> my concern is not breaking linearity (as actually the estimation is still
> linear). It's more that you apply this in a setup with a big tall matrix
> which should be well conditionned. To support more advanced estimators then
> the API should be changed to support sklearn estimators.
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/mne-tools/mne-python/pull/2304#issuecomment-122224890
> .


--- Comment 20 by choldgraf ---
Yes - usually if I want to assess model stability I will fit, say, 30
models on random subsets of trials, then look at the z-scores for each
feature across all CVs. If you want to make it take way longer, you can
also do GridSearch for regularization parameters, but this can take forever.

On Fri, Jul 17, 2015 at 11:21 AM, Denis A. Engemann <
notifications@github.com> wrote:

> We just discussed with Alex and came to the conclusion that computing a
> source estimate on ERP/Fs computed with regularized regresison should still
> be valid but you should mnot compute classical statistics on it, such as
> t-statistics that you would compute with a standard GLM. Once you
> regularize you move from an estimation to a precition regime (cross
> validation, etc.).
> 
> On Fri, Jul 17, 2015 at 11:07 AM, Alexandre Gramfort <
> notifications@github.com> wrote:
> 
> > my concern is not breaking linearity (as actually the estimation is still
> > linear). It's more that you apply this in a setup with 

--- END ---