# ENH: draft of mne report command (#1261)
URL: https://github.com/mne-tools/mne-python/pull/1261
State: closed | PR: YES
Comments: 142 | Created: 2014-05-05T13:57:41Z | Closed: 2014-07-19T12:18:50Z

## Body (first 1000 chars)
Closes https://github.com/mne-tools/mne-python/issues/1056 

Try

``` sh
 mne report -p MNE-sample-data/ -i MNE-sample-data/MEG/sample/sample_audvis-ave.fif -d MNE-sample-data/subjects/ -s sample -x -v
```

and it should generate `report.html` in `MNE-sample-data/`

Sample output here: https://dl.dropboxusercontent.com/u/3915954/report.html
## TODOS
- [x] recursive exploration
- [x] rebase and use read_evokeds
- [x]  extend the support to as many fif files types 
  - [x] cov
  - [x] fwd 
  - [x] inv
  - [x] raw
  - [x] trans (display head in helmet to check coregistration quality in `mne.viz.plot_trans()`)
  - [x] epo : plot_drop_log
- [ ] check dpi settings
- [x] Slicer coordinates
- [x] Table of contents linking to different parts of html?
- [x] the bootstrap/JS theme should allow to select which type of fif file to display. See jquery toggle
- [x] also bad fif files should appear in red for example if the fif fname is not standard (evoked should end with -ave.fif, cov with -cov.fif,

## Comments

--- Comment 1 by agramfort ---
can you update the PR header with tick boxes with the todos that comes to mind?


--- Comment 2 by mainakjas ---
@agramfort @dengemann : what do we do about viewing raw data? sliders in mne_browse_raw style? writing binary images may be very cumbersome -- should we hack something in d3 ? something like this: https://github.com/mbostock/d3/wiki/Zoom-Behavior +  tempita. Any other suggestions?


--- Comment 3 by agramfort ---
for now for the Raw just print the REPR and the info repr

a javascript raw browser is beyond the scope for a minimal working PR


--- Comment 4 by agramfort ---
+1 for Table of contents linking to different parts of html

the bootstrap/JS theme should allow to select which type of fif file to display. See jquery toggle

also bad fif files should appear in red for example if the fif fname is not standard (evoked should end with -ave.fif, cov with -cov.fif, raw with raw.fif or sss.fiff etc....)


--- Comment 5 by mainakjas ---
ok, we now have a table of contents + bad file names in red. Does `mne.fiff.read_evokeds` have a `verbose` option ? Because I want to turn off logging for that.


--- Comment 6 by agramfort ---
> Does mne.fiff.read_evokeds have a verbose option ? Because I want to turn off logging for that.

if not please open a PR to fix this. Or maybe wait for the io module PR to be merged to avoid a merging/rebasing mess...


--- Comment 7 by agramfort ---
how about a black banner on top as in :

http://getbootstrap.com/examples/jumbotron/

that says "MNE Report for /path/to/folfer"

in the footer a link saying

"Powered by MNE"

with a link to martinos.org/mne

just coming up with ideas to make it nice and look pro :)


--- Comment 8 by agramfort ---
you should also think of how to render the -trans.fif files.

it would be great to display head in helmet to check coregistration quality. You'll need a bit of work to make it work. I recommend to do it in another PR with a mne.viz.plot_trans function.


--- Comment 9 by larsoner ---
+1, that would be awesome. I can also work on this if @mainakjas your time is better spent elsewhere. If you do want to work on it, all the transformations, surfaces, and their relationships that you need you can dig out of the field lines example.


--- Comment 10 by mainakjas ---
Thanks @agramfort @Eric89GXL. I am just updating the mne-report with the navbar + footer as we speak + some other minor modifications. Nice idea about checking coregistration quality but I'll check in a day or two to estimate how much effort is required there.


--- Comment 11 by agramfort ---
Another idea is to open the report in a browser when generated. Look at how "ipython notebook" does it


--- Comment 12 by mainakjas ---
ok, sounds good. I have now added the navbar + footer. The button toggling has been included in the navbar now such that all buttons (eve, cov etc) are in the "on" state initially but the user can turn them off as required.


--- Comment 13 by mainakjas ---
would you be ok with a dependency on `splinter` ? I know that can open the browser from python. Not sure if there are other ways.


--- Comment 14 by maedoc ---
> open browser from Python

Fwiw, this is part of [`webbrowser`](https://docs.python.org/2.7/library/webbrowser.html) in the standard library:

``` python
import webbrowser
webbrowser.open_new_tab("http://localhost:8888")
```


--- Comment 15 by agramfort ---
beautiful !

thanks for the tip


--- Comment 16 by mainakjas ---
@agramfort : just to be sure, what are the coordinates X, Y, Z? Do we need those since the slider values are displayed below the image anyway?


--- Comment 17 by mainakjas ---
also, what about the color map selector for *.mgz files? I suppose that'll blow the size of the html file exponentially. Maybe we should just expose the option of selecting color map from python and not html?


--- Comment 18 by agramfort ---
Drop cmap support and use only gray


--- Comment 19 by agramfort ---
> @agramfort : just to be sure, what are the coordinates X, Y, Z? Do we need those since the slider values are displayed below the image anyway?

Probably not


--- Comment 20 by agramfort ---
any progress here?

you should address the plot_trans function but in a different PR.

another PR you could write is one that throws warning with saving and reading fif files with non-standard extensions. To force gently the use of our conventions...


--- END ---