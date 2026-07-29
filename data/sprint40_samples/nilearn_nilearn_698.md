# [WIP] Decoder: Metaestimator (#698)
URL: https://github.com/nilearn/nilearn/pull/698
State: closed | PR: YES
Comments: 28 | Created: 2015-07-17T08:30:59Z | Closed: 2020-03-09T12:36:41Z

## Body (first 1000 chars)
High-level decoding object that exposes standard classification and regression strategies such as SVM, LogisticRegression and Ridge, with optional feature selection, and integrated parameter selection.

In other words, this object implements the pipeline:  
masking + feature selection (screening) + estimation (parameter selection and model averaging)

Haxby dataset, face  > house (similar to [Haxby face > cat](http://nilearn.github.io/auto_examples/plot_haxby_simple.html))
"full brain"
estimator =  'ridge_classifier'
screening_percentile = 20

![coef](https://cloud.githubusercontent.com/assets/6594763/8743369/8b8560d0-2c6e-11e5-9d19-aefe1a345c03.png)

Oasis dataset, age prediction (same as [OASIS example](http://nilearn.github.io/auto_examples/decoding/plot_oasis_vbm.html))
estimator =  'ridge_regression'
screening_percentile = 2 

![weights](https://cloud.githubusercontent.com/assets/6594763/8743374/95d5122e-2c6e-11e5-8065-b1c4fec53342.png)


## Comments

--- Comment 1 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209048/landscape.svg?style=flat)](https://landscape.io/diff/197883)
Repository health decreased by 0.35% when pulling **[848392c](https://github.com/ahoyosid/nilearn/commit/848392ca378364579fcb0d5d1883d9f4f986e686) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [20 new problems were found](https://landscape.io/diff/197883) (including 1 error and 10 code smells).
- No problems were fixed.


--- Comment 2 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209048/landscape.svg?style=flat)](https://landscape.io/diff/197883)
Repository health decreased by 0.35% when pulling **[848392c](https://github.com/ahoyosid/nilearn/commit/848392ca378364579fcb0d5d1883d9f4f986e686) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [20 new problems were found](https://landscape.io/diff/197883) (including 1 error and 10 code smells).
- No problems were fixed.


--- Comment 3 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209048/landscape.svg?style=flat)](https://landscape.io/diff/197883)
Repository health decreased by 0.35% when pulling **[848392c](https://github.com/ahoyosid/nilearn/commit/848392ca378364579fcb0d5d1883d9f4f986e686) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [20 new problems were found](https://landscape.io/diff/197883) (including 1 error and 10 code smells).
- No problems were fixed.


--- Comment 4 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209048/landscape.svg?style=flat)](https://landscape.io/diff/197883)
Repository health decreased by 0.35% when pulling **[848392c](https://github.com/ahoyosid/nilearn/commit/848392ca378364579fcb0d5d1883d9f4f986e686) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [20 new problems were found](https://landscape.io/diff/197883) (including 1 error and 10 code smells).
- No problems were fixed.


--- Comment 5 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209632/landscape.svg?style=flat)](https://landscape.io/diff/198266)
Repository health decreased by 0.36% when pulling **[97514e9](https://github.com/ahoyosid/nilearn/commit/97514e9c3029697ad5a21b700b09913d5018eeb8) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [22 new problems were found](https://landscape.io/diff/198266) (including 1 error and 12 code smells).
- [2 problems were fixed](https://landscape.io/diff/198266/fixed) (including 0 errors and 2 code smells).


--- Comment 6 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209637/landscape.svg?style=flat)](https://landscape.io/diff/198272)
Repository health decreased by 0.33% when pulling **[63835f2](https://github.com/ahoyosid/nilearn/commit/63835f27bc7de5026194a6ecb9dfda3f00ed6434) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [18 new problems were found](https://landscape.io/diff/198272) (including 2 errors and 7 code smells).
- [1 problem was fixed](https://landscape.io/diff/198272/fixed) (including 0 errors and 1 code smell).


--- Comment 7 by landscape-bot ---
[![Code Health](https://landscape.io/badge/209643/landscape.svg?style=flat)](https://landscape.io/diff/198279)
Repository health decreased by 0.22% when pulling **[10aa812](https://github.com/ahoyosid/nilearn/commit/10aa812f02f7ca9e96a419948adfe7ff25cebb1a) on ahoyosid:decoder** into **[08f023a](https://github.com/nilearn/nilearn/commit/08f023a6185b66647eb1e0b0baa2d0e6e729c0a9) on nilearn:master**.
- [15 new problems were found](https://landscape.io/diff/198279) (including 1 error and 6 code smells).
- [1 problem was fixed](https://landscape.io/diff/198279/fixed) (including 0 errors and 1 code smell).


--- Comment 8 by eickenberg ---
Just a thought for the `__future__` (after these PRs are merged): Could the univariate feature screening deluxe from spacenet be useful here? If so, wouldn't a feature screener be a target-oriented type of masker?


--- Comment 9 by codecov[bot] ---
# [Codecov](https://codecov.io/gh/nilearn/nilearn/pull/698?src=pr&el=h1) Report
> Merging [#698](https://codecov.io/gh/nilearn/nilearn/pull/698?src=pr&el=desc) into [master](https://codecov.io/gh/nilearn/nilearn/commit/2f825c480f6f7c9fbf4873e81121c4320dedd71d?src=pr&el=desc) will **decrease** coverage by `0.38%`.
> The diff coverage is `78.08%`.

[![Impacted file tree graph](https://codecov.io/gh/nilearn/nilearn/pull/698/graphs/tree.svg?src=pr&token=KpYArSdyXv&width=650&height=150)](https://codecov.io/gh/nilearn/nilearn/pull/698?src=pr&el=tree)

```diff
@@            Coverage Diff             @@
##           master     #698      +/-   ##
==========================================
- Coverage   94.66%   94.28%   -0.39%     
==========================================
  Files         120      123       +3     
  Lines       14686    14985     +299     
==========================================
+ Hits        13903    14129     +226     
- Misses        783      856      +73
```


| [Impact

--- Comment 10 by GaelVaroquaux ---
>     Merging #698 into master will decrease coverage by 2.04%.
>     The diff coverage is 27.46%.

I wonder if the coverage is not a bit low on this PR.


--- Comment 11 by banilo ---
Besides the comments above, a global change that could be added:
The Decoder could further facilitate useability of nilearn in many everyday decoding scenarios by setting the *hyper-parameter grids* for the estimators automatically. That would come in handy.

--- Comment 12 by GaelVaroquaux ---
> +   Decoder

> Shouldn't this rather be "DecoderClassifier" analogous to the sklearn conventions?

I thought that this would be simpler, and that 90% of the decoding
applications are classification.


--- Comment 13 by KamalakerDadi ---
You have missed to found some target in ```doc/building_blocks/manual_pipeline.rst``` related to example
plot_decoding_tutorial. Hence the CircleCI failure. Could you have a look at it ?

Please ping me whenever it is ready to review.

--- Comment 14 by ahoyosid ---
@KamalakerDadi I actually have not idea what this conflict is about, any insights?

--- Comment 15 by KamalakerDadi ---
>@KamalakerDadi I actually have not idea what this conflict is about, any insights?

I didn't get you. Which conflict ?

--- Comment 16 by ahoyosid ---
The circle ci failure

--- Comment 17 by KamalakerDadi ---
>The circle ci failure

For me there is no problem with the failure which CircleCI shows in "doc/building_blocks/manual_pipeline.rst" related to WARNING: image file not readable: building_blocks/../auto_examples/images/sphx_glr_plot_decoding_tutorial_002.png.

 I ran locally everything and it seems good for me that file is read in the doc, see pics below:

![decoder](https://cloud.githubusercontent.com/assets/11410385/25776145/88233eda-32b6-11e7-87b0-a4ccf72aa4cc.png)

![decoder2](https://cloud.githubusercontent.com/assets/11410385/25776146/8c2978a0-32b6-11e7-8c64-9043753ea3f8.png)

Could you try rebasing, may be ?


--- Comment 18 by KamalakerDadi ---
FYI: We dropped sklearn < 0.15.

--- Comment 19 by kchawla-pi ---
Is this alive? If not, please close it by this weekend.

--- Comment 20 by KamalakerDadi ---
I would like to take this over. Any objections ?

--- END ---