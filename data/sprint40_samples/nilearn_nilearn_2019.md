# [ENH] Initial visual reports (#2019)
URL: https://github.com/nilearn/nilearn/pull/2019
State: closed | PR: YES
Comments: 172 | Created: 2019-04-17T13:58:44Z | Closed: 2019-10-02T10:49:46Z

## Body (first 1000 chars)
Closes #2022 .

An initial implementation of visual reports for Nilearn. Adds:
- [x] The templating library _tempita_ as an external dependency
- [x] A reorganization of `HTMLDocument` into a new `reporting` module
- [x] A new reporting HTML template
- [x] A super class `Report` to populate the report HTML template with _tempita_ populated text
- [x] Relevant CSS styling to improve report UX, using [pure-css](https://purecss.io/)
- [x] An ability to display reports directly in Jupyter Notebooks, without iframe rendering, thanks to @GaelVaroquaux 
- [x] Documentation of this functionality, with examples
- [x] A new [Sphinx Gallery image scraper](https://sphinx-gallery.github.io/advanced.html#write-a-custom-image-scraper) to embed these example HTML reports

For a current rendering of reports see: https://github.com/emdupre/nilearn/pull/4#issuecomment-527984327 and the [`plot_mask_computation` example](https://4703-1235740-gh.circle-artifacts.com/0/home/circleci/project/doc/_

## Comments (first 1000 chars each)

--- Comment 1 by jeromedockes ---
thanks! is there an issue or a discussion somewhere describing what these reports will contain?

--- Comment 2 by GaelVaroquaux ---
> is there an issue or a discussion somewhere describing what these reports will contain?

No, and we should create one.

@emdupre, can you do it?


--- Comment 3 by jeromedockes ---
> No, and we should create one.

it can also be a quick summary in the conversation of this PR

--- Comment 4 by jeromedockes ---
>  [emdupre](/emdupre) referenced this pull request [ 25 minutes ago ](#ref-issue-434325568)

thanks! 

--- Comment 5 by emdupre ---
@GaelVaroquaux the Travis is failing for a vendoring issue -- if you have any suggestions, please LMK !

--- Comment 6 by jeromedockes ---
`import tempita` will look for tempita in the python path and not find it. since
you are vendoring it you need to import it from nilearn.externals: `from
nilearn.externals import tempita`

--- Comment 7 by GaelVaroquaux ---
I made a PR on your PR:
https://github.com/emdupre/nilearn/pull/1

More responsive layout inside the notebook.

--- Comment 8 by GaelVaroquaux ---
Thanks for taking care of the merge!

I think that we will need to reorganize the files and imports. Currently the code is not broken out in a sensible way.

I suggest that we create a "nilearn.reporting" subpackage to move out of plotting the HTMLDocument class. Indeed, as it is currently in nilearn.plotting, importing it draws in an import of matplotlib. We could move in the HTMLReport next to the HTMLDocument (and maybe remove it HTMLSnippet ?). We could move in there also all the machinery for reporting. We would add delayed imports to plotting (ie imports inside the function).

Ping @jeromedockes for comments on the suggested reorg

--- Comment 9 by jeromedockes ---
I am in favor of keeping nilearn core functionality and reporting completely
separate, or as separate as possible. a user can get by without the reporting,
so issues with the reporting should not interfere with essential functionality.
for example right now the simplest possible use of NiftiMasker fails:


```
from nilearn import input_data, datasets
masker = input_data.NiftiMasker(datasets.load_mni152_brain_mask()).fit()
```
raises a `TypeError`.

I would prefer if the only changes to core functions of nilearn were storing
additional information (which requires no computation, and definitely no
plotting), and all the reporting be done in the reporting package.

--- Comment 10 by jeromedockes ---
I wonder if other browser-web plots would benefit from changes made by
@GaelVaroquaux to keep the head and bodies of documents separate?

--- Comment 11 by jeromedockes ---
one remark about the iframes: one benefit is to have our plots completely
isolated from the rest of the page, e.g. other versions of the javascript
libraries we use etc. right now the reports use no javascript; will that always
be the case?

--- Comment 12 by jeromedockes ---
@emdupre could you add a tiny example to easily generate a report that we can use while discussing this PR? it could be as simple as 
```
from nilearn import input_data, datasets, plotting
mni = datasets.load_mni152_template()
masker = input_data.NiftiMasker().fit([mni, mni])
plotting.generate_report(masker).save_as_html('/tmp/report.html')
```

--- Comment 13 by GaelVaroquaux ---
Maybe. However JavaScript injection is blocked in jupyter lab. Hence the risk is that they don't work in jupyter lab.

Maybe this is also the case for CSS. I don't think so, but it would be good to check. 

⁣Sent from my phone. Please forgive typos and briefness.​

On May 2, 2019, 14:44, at 14:44, jeromedockes <notifications@github.com> wrote:
>I wonder if other browser-web plots would benefit from changes made by
>@GaelVaroquaux to keep the head and bodies of documents separate?
>
>-- 
>You are receiving this because you were mentioned.
>Reply to this email directly or view it on GitHub:
>https://github.com/nilearn/nilearn/pull/2019#issuecomment-488657810


--- Comment 14 by GaelVaroquaux ---
Good point. These css are small. They should be shipped with nilearn. 

⁣Sent from my phone. Please forgive typos and briefness.​

On May 2, 2019, 14:51, at 14:51, jeromedockes <notifications@github.com> wrote:
>jeromedockes commented on this pull request.
>
>
>
>> @@ -0,0 +1,104 @@
>+<!-- CSS for the report -->
>+<link rel="stylesheet"
>href="https://unpkg.com/purecss@1.0.0/build/pure-min.css"
>integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w"
>crossorigin="anonymous">
>
>right now other browser-based plots in nilearn work offline. how big is
>pure-min.css, could it be shipped with nilearn? 
>
>-- 
>You are receiving this because you were mentioned.
>Reply to this email directly or view it on GitHub:
>https://github.com/nilearn/nilearn/pull/2019#pullrequestreview-232986822


--- Comment 15 by GaelVaroquaux ---
> as @GaelVaroquaux if we really cannot avoid doing any plotting here this must
> be delayed to inside the reporting functions. most of nilearn can be used
> without matplotlib installed

An option would be to create functions in nilearn.reporting that mirror
the basic plotting functions but return the html string. These would be
"safe" in the sense that they don't crash, but return a different
(hopefully useful) string if matplotlib is not present.



--- Comment 16 by GaelVaroquaux ---
> I would prefer if the only changes to core functions of nilearn were storing
> additional information (which requires no computation, and definitely no
> plotting), and all the reporting be done in the reporting package.

While I agree that nilearn needs to be perfectly safe to use without
reporting, I feel that object-oriented paradigm is the right tool here:
each object will know the specificities of how it should be "reported". I
do think that a reporting method makes sense. We just need to make it
safe. This should probably be feasible with tests.



--- Comment 17 by GaelVaroquaux ---
> one remark about the iframes: one benefit is to have our plots completely
> isolated from the rest of the page, e.g. other versions of the javascript
> libraries we use etc.

Yes! Absolutely. I like them for this.

> right now the reports use no javascript; will that always be the case?

I would like to try doing reporting without javascript. For some objects
at least it should be possible. Maybe all?


--- Comment 18 by jeromedockes ---
> For some objects at least it should be possible. Maybe all?

probably, although in some cases maybe the brainsprite viewer can be useful?

--- Comment 19 by GaelVaroquaux ---
> probably, although in some cases maybe the brainsprite viewer can be useful?

Agreed. But it will also cost more in terms of kilobytes and time to
generate. I think that we want these reports to be safe to use, so that
they are often used. One think that I would worry about is notebook
becoming too heavy (it already tends to be the case without the reports).

However, yes, maybe we will consider in the long term, in some cases, to
embed it. I would leave it out for now.


--- Comment 20 by emdupre ---
> Maybe. However JavaScript injection is blocked in jupyter lab. Hence the risk is that they don't work in jupyter lab. Maybe this is also the case for CSS. I don't think so, but it would be good to check.

Seems like, indeed, it's not the case for CSS if we package it ourselves: https://github.com/jupyterlab/jupyterlab/issues/3200#issuecomment-342874961

--- END ---