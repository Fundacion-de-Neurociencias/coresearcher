# [MRG] Dictionary learning + nilearn.decomposition refactoring (#693)
URL: https://github.com/nilearn/nilearn/pull/693
State: closed | PR: YES
Comments: 51 | Created: 2015-07-16T15:36:20Z | Closed: 2015-12-08T14:44:07Z

## Body (first 1000 chars)
Decomposition estimators (`DictLearning` / `MultiPCA`) now inherit a  `DecompositionEstimator`.

Loading of data is made through a `PCAMultiNiftiMasker`, which loads data from files and compress it.

Potentially, the function check_masker could solve issue #688, as it factorizes the input checking of estimator to which you provide either a masker or parameters for a mask. It is tuned to be able to use `PCAMultiNiftiMasker`


## Comments

--- Comment 1 by AlexandreAbraham ---
As a general matter, I am not comfortable with the "pipelining through inheritance" pattern. Especially because it is not easy to combine it with out caching system.

What we have now in nilearn.decomposition.MultiPCA is:
- MultiPCA takes a MultiNiftiMasker as parameter (or directly a mask, this is not the point here)
- It masks data and runs a PCA on the masked data.
- Its associated function, session_pca, takes niimgs as parameter, calls filter_and_mask and runs the PCA afterward. We can easily cache the call to session_pca because most of the time niimgs are strings.
- However, if we want to add more steps to the pipeline (ie CanICA), we have to inherit from MultiPCA and thus we don't have access to intermediate data, the masked data in our case.

What is proposed in this PR:
- PCAMultiNiftiMasker inherits from MultiNiftiMasker
- MultiPCA is now almost empty, it is just a wrapper around PCAMultiNiftiMasker
- nothing has changed regarding session_pca function.

What I think is the wa

--- Comment 2 by GaelVaroquaux ---
>   • SinglePCA is a transformer that takes masked data and returns their PCA.

The problem with this is that it forces to do things with the wrong
parallel-execution layout: you would have to load and mask all the data,
then do SVDs. Both in terms of parallel execution (imposing a barrier
between loading and SVDs) and in terms of memory usage (storing the data
in memory).

I tend to think that the basic element of reuse for stateless pipeline
operations is much more the function than the class. Indeed, objects are
not needed to keep state (the only reason that the Transformer is an
object is because it has separate fit and transform stages, and needs to
keep a state between the two). Functions lead to code reuse with less
boilerplate.


--- Comment 3 by arthurmensch ---
I moved the fast concatenation to a separate `_utils` function. For the moment you can observe than `multi_pca` and `dict_learning` has a few common lines that could be factorized, but I think that these belongs to the own logic of both objects so it may not be worth.

In term of merging strategy, I merged PR #702 for testing purpose on this PR, but I can remove the commits for this PR easily, so we can merge this PR on top of PR #702


--- Comment 4 by lesteve ---
Needs a rebase + failing tests.


--- Comment 5 by arthurmensch ---
> MultiPCA is a transformer. It has init parameters of both MultiNiftiMasker and SinglePCA. It creates instances of both of them and, on fit, streamline the process: it takes the niimgs as input, mask them in the MNMasker, gives the masked data to the SinglePCA and aggregates the results, doing a cca if asked. Obviously, this is run online and efficiently (njobs and stuff)

This is basically what is done with make_pca_masker : streamline is done within function `session_pca`, instead of setting up a explicit pipe between two transformers. Trouble being that if we want to do that, we need to use MultiNiftiMasker.transform_single_imgs, piped to randomized_pca, which forces use to use Parallel over an already parallel ready object (MultiNiftiMasker)


--- Comment 6 by AlexandreAbraham ---
Since your PR is working and improving code organization, I suggest that we go for merge and discuss of code engineering afterward. I don't want this PR to be blocked like Elvis' and the inner code won't change anything for the user.


--- Comment 7 by AlexandreAbraham ---
Honestly, I don't see why we have `make_pca_masker` and `PCAMultiNiftiMasker` where we could just use `MultiNiftiMasker` followed by a PCA. We never make pipelines out of transformers, we make pipelines by using the functions on which the transformers depend.

Current state:
- MultiNiftiMasker
  - `fit` calls `filter_and_mask`
- MultiPCA
  - `fit` calls `session_pca`
  - `session_pca` calls `filter_and_mask`
- CanICA
  - `fit` calls `MultiPCA.fit`
  - `fit` then does the work

Proposition:
- MultiNiftiMasker
  - `fit` calls `filter_and_mask`
- SinglePCA
  - `fit` calls`single_pca` that takes as input masked data and do a PCA
- MultiPCA
  - `fit` calls `session_pca`
  - `session_pca` chains `filter_and_mask` and `single_pca`
- CanICA
  - `fit` calls `canica`
  - `canica` calls `session_pca`, and then `single_pca` and does ica afterward.
  - Note : this is optional.
- DictLearning
  - `fit` calls `dict_learning`
  - `dict_learning` calls `filter_and_mask` can easily do the job if init is

--- Comment 8 by GaelVaroquaux ---
> Honestly, I don't see why we have make_pca_masker and PCAMultiNiftiMasker where
> we could just use MultiNiftiMasker followed by a PCA.

Once again: parallel computing + memory conception.


--- Comment 9 by eickenberg ---
> We never make pipelines out of transformers, we make pipelines by using
> the functions on which the transformers depend.

It is however imaginable that some such transformers may need spatial
information. I am thinking specifically about the feature screening
currently only used in SpaceNet but which in the future could very well
serve for other estimators as well. In this case it would need to be inside
the masker.

On Tue, Jul 21, 2015 at 11:51 AM, Gael Varoquaux notifications@github.com
wrote:

> > Honestly, I don't see why we have make_pca_masker and
> > PCAMultiNiftiMasker where
> > we could just use MultiNiftiMasker followed by a PCA.
> 
> Once again: parallel computing + memory conception.
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/nilearn/nilearn/pull/693#issuecomment-123245049.


--- Comment 10 by AlexandreAbraham ---
> Once again: parallel computing + memory conception.

Well, no this is not the reason because the code behind the scenes is unchanged, this is only a refactoring the class organization where a part of MultiPCA becomes a class itself.

OK, it took me some time but now I get it. I'm not happy with `make_pca_masker` (I think that you could always use a PCAMultiNiftiMasker and decide to do the PCA or not inside) and I'm not happy with the naming, but I can live with that ;).


--- Comment 11 by AlexandreAbraham ---
>  In this case it would need to be inside the masker.

It would precisely need to be inside the masker, after the smoothing and before the cleaning. So, just where the masking is. This is precisely the code pattern I introduced in #665 and that allows to define NiftiMasker, NiftiLabelsMasker, or even NiftiUnivariateScreeningMasker if you want, using the same piece of code. Here, we are talking about software design for a PCA after masking. To summarize it, if masking and pca were 2 boxes, the actual choice is put the masking box inside the pca box. For me, it's not the best choice given that if you want to add another step, then you'll need a bigger box. I see that as boxes put next to each other.

But that's my personal bias, I am aware of that and I am totally opened to other solutions. I am just arguing a bit here because, in my head, I see a very simple schema and my impression here is that the spaghetti code has been replaced by lasagna code.


--- Comment 12 by AlexandreAbraham ---
In particular, the concept itself of MultiNiftiMasker in the MultiPCA is a fraud: we use it to compute the mask, in the fit, that's a fact. But we don't use it for masking at all. For that, we basically use a NiftiMasker chained with a PCA in a parallel loop.


--- Comment 13 by AlexandreAbraham ---
Talking with Arthur, we have identified the same weaknesses in the approach of software design in nilearn. Since his PR is an enhancement compared to existent, I suggest that we merge it and we discuss software refactoring after since it's another subject.


--- Comment 14 by lesteve ---
Your example doesn't work with python 3 for some reason I don't really understand. In the traceback below `n_iter` is a float (2085.16... if you want to know). The fact that it was not caught by the tests is not really reassuring:

```
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
/home/le243287/dev/nilearn/examples/connectivity/plot_dict_learning_resting_state.py in <module>()
     53     print('[Example] Learning maps using %s model'
     54           % type(estimator).__name__)
---> 55     estimator.fit(func_filenames)
     56     print('[Example] Dumping results')
     57     components_img = estimator.masker_.inverse_transform(estimator.components_)

/home/le243287/dev/nilearn/nilearn/decomposition/dict_learning.py in fit(self, imgs, y, confounds)
    209             random_state=self.random_state,
    210             shuffle=True,
--> 211             n_jobs=1)
    212        

--- Comment 15 by arthurmensch ---
i guess I should push the coverage to 100%


--- Comment 16 by arthurmensch ---
I came up with a simpler design for handling data loading (using a memory map if the dataset is too big) before performing dictionary_learning or Group PCA.

The idea is that you need to load the data line by line before performing a dictionary learning column by column. Using a memorymap to store masked data in this context allows us not to blow the memory over when working on big datasets (e.g. ADHD 40 subjects on 4GB machine).

In this design `mask_and_reduce` does the job of `session_pca` + concatenates data from the `imgs` list, either in a ndarray or memorymap. I think it should be decorated as a context manager so as to handle temp file removal at the end of the different `fit` methods.

The goo thing is that we do not need ugly abstraction like  `PCAMultiNiftiMasker` or `make_pca_masker`

Reviews would be welcomed !


--- Comment 17 by arthurmensch ---
With this PR + `scikit-learn` master we are able to run dictionary learning on 40 subject of ADHD in 90s doing two epochs (recent change on scikit-learn dictionary learning module makes it much faster using coordinate descent). From far, the most costly part of the algorithm becomes masking.

I believe that out-of-core computation of unmasked data is not yet completely possible, as data is entirely copied in `randomized_svd`, when performing `CanICA` optimization. This could be sorted using `IncrementalPCA` instead.

We could also gain in perf by parallelizing `mask_and_reduce`, if `filter_and_mask` is CPU-bounded.


--- Comment 18 by AlexandreAbraham ---
On test seems to be failing (which is weird because travis is happy). Apart from small details, LGTM.


--- Comment 19 by AlexandreAbraham ---
Failing test is : 

```
File "/home/ubuntu/nilearn/nilearn/decomposition/tests/test_dict_learning.py", line 49, in test_dict_learning
    assert_true(recovered_maps >= 2)
```

Please use proper functions (something like `assert_less`) to get more accurate errors.


--- Comment 20 by lesteve ---
I don't know why codacy doesn't send PR status anymore but you seem to have a few PEP8 violations. See https://www.codacy.com/app/lesteve/nilearn/pullRequest?prid=70136.


--- END ---