# (WIP) Sparse models: S-LASSO and TV-l1 (#219)
URL: https://github.com/nilearn/nilearn/pull/219
State: closed | PR: YES
Comments: 78 | Created: 2014-06-27T09:16:58Z | Closed: 2015-07-14T07:45:53Z

## Body (first 1000 chars)
- Supports TV-l1 and S-LASSO priors
- Supports logistic and squared losses
- Has cross validation
- Can automatically select alpha by CV (+ automatic computation of useful alpha ranges for the CV)
- Warning: User must supply l1_ratio


## Comments

--- Comment 1 by dohmatob ---
# Class diagram

![classes_sparse_models](https://cloud.githubusercontent.com/assets/634068/3409868/937144fe-fdde-11e3-82ce-433755f0b579.png)

# Modules inter-dep

![packages_sparse_models](https://cloud.githubusercontent.com/assets/634068/3409871/98fc6b1a-fdde-11e3-8c21-e7c7fec42720.png)

This should help figure out what to refactor into / out of, what.


--- Comment 2 by agramfort ---
prox_tv_l1.py should be merged with operators.py


--- Comment 3 by agramfort ---
no example with TV L1?


--- Comment 4 by agramfort ---
tests pass in 5s on my box + 88% coverage. Good job.

just a note on the smooth lasso example I am not really able to see something on the score graph.

that's it for me now


--- Comment 5 by dohmatob ---
Example for TV-l1 will follow asap.

The score graph (CV) says: "the given haxby classif problem does not really like our spatial prior", and at one point it gets fed up with it altogether and destroys the model (utterly bad predictions).

I'll need to check on another dataset (oasis for example), to roll out the possibility of there being a bug in the CV logic :)


--- Comment 6 by agramfort ---
how about poldrack's data?


--- Comment 7 by dohmatob ---
Results look good on PMG. I've not included it yet in nilearn because there is no fetcher. Indeed,
![pmg_cv](https://cloud.githubusercontent.com/assets/634068/3414488/65b8c130-fe16-11e3-9417-640e297784f5.png)
![pmg_map](https://cloud.githubusercontent.com/assets/634068/3414492/729ffc74-fe16-11e3-93e5-7ba83f3af240.png)


--- Comment 8 by agramfort ---
can you share with me your script on PMG?


--- Comment 9 by dohmatob ---
Here: parietal-pHython / examples / proximal / plot_poldrack_smoothlasso.py


--- Comment 10 by dohmatob ---
@agramfort: Thanks for the useful comments. I'll address them asap. Also, I'd like to have your say on issue #220


--- Comment 11 by dohmatob ---
# Oasis VBM proof-of-concept

![oasis_weights](https://cloud.githubusercontent.com/assets/634068/3420401/10734064-fea8-11e3-868a-8da9a91d674a.png)
![oasis_cv](https://cloud.githubusercontent.com/assets/634068/3420403/182e546a-fea8-11e3-89af-f55b0a4cabc1.png)
![oasis_errors](https://cloud.githubusercontent.com/assets/634068/3420440/79b1ac22-fea9-11e3-8fc8-834afd71a2f8.png)


--- Comment 12 by agramfort ---
pretty nice !

the selected alpha seems a bit weird to me. I thought that Gael wanted to
select one alpha per fold and average the weights rather than refit?


--- Comment 13 by dohmatob ---
The legend about the selected alpha is just for information. The grand final weights map is still an average of the maps corresponding to the best models per fold, as intended. So we are fine. Good remark though.


--- Comment 14 by agramfort ---
ok let me know when I shall review again.


--- Comment 15 by dohmatob ---
OK, I'll have a look after launch.


--- Comment 16 by dohmatob ---
@agramfort  You may resume reviewing.


--- Comment 17 by GaelVaroquaux ---
As a general comment, I think that the sparse_model folder should be a sub-folder of the 'decoding' folder.


--- Comment 18 by dohmatob ---
Ok.


--- Comment 19 by agramfort ---
@dohmatob let us now when you're done addressing all our comments


--- Comment 20 by dohmatob ---
Hurray! "TV-l1" deconvolution using an appropriate primal-dual (re-)formulation. In a sense, this is the 'optimal' scheme (the 'book' scheme) for this long lasting problem... Ping @agramfort. The code will follow soon.

Remark: Smooth lasso is (it seems to me) the ultimate Occam's razor for the "structure" + "sparsity" prior.

![tvl1_weights](https://cloud.githubusercontent.com/assets/634068/3535480/908e2e64-0801-11e4-8f45-6d69ca31f135.png)
![tvl1_folds](https://cloud.githubusercontent.com/assets/634068/3535483/998d4126-0801-11e4-94d3-5795bb8e6de6.png)


--- END ---