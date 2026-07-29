# [MRG+2] adding receptive field module (#3728)
URL: https://github.com/mne-tools/mne-python/pull/3728
State: closed | PR: YES
Comments: 191 | Created: 2016-11-03T16:06:18Z | Closed: 2017-03-29T02:21:27Z

## Body (first 1000 chars)
Just when you thought it was safe, it returns! Unnecessarily complicated API changes make a comeback in "Gitastrophe 2: Attack of the clone(d repository)"

This is a new branch off of master and a greatly simplified version of the long discussion in #2796. The basic idea is that we decided tackling the general encoding model problem is probably too much to bite off in one PR, especially when the sklearn API might change somewhat. This is a PR to add a receptive field module. It includes some (unfinished) tests, a new class, a few new functions, and an example.

LMK

@agramfort @Eric89GXL @kingjr @jona-sassenhagen 

Closes #2796.

## Comments (first 1000 chars each)

--- Comment 1 by agramfort ---
CIs are not happy


--- Comment 2 by choldgraf ---
Hey all - let me know if comments are done and I can make changes. Travis isn't happy because I haven't finished uncovering bugs and writing tests. If you guys think the API (in general) is OK then I will move forward on the smaller changes and specific suggestions...


--- Comment 3 by larsoner ---
I haven't had a chance to really look into the API yet. I want to see if it's possible to make use of the more efficient routines. I wonder if it's worth making the API more restrictive to start (e.g., force just a start and stop time, instead of allowing arbitrary indices) so we can make it efficient.


--- Comment 4 by choldgraf ---
If we're using sklearn under the hood, then I feel like forcing people to
use all possible lags between a tmin and tmax will make it slower (e.g. if
my sampling frequency is 10x higher, then I'll have 10x more features in
the model now). If there's a more clever way of finding the coefficients
solution, then maybe that'd work fine.

Though we are now getting back into the weeds of lots of conversations that
we had back in the franken-PR of the general encoding models stuff...

## 

On Fri, Nov 4, 2016 at 6:13 PM Eric Larson notifications@github.com wrote:

I haven't had a chance to really look into the API yet. I want to see if
it's possible to make use of the more efficient routines. I wonder if it's
worth making the API more restrictive to start (e.g., force just a start
and stop time, instead of allowing arbitrary indices) so we can make it
efficient.

—
You are receiving this because you authored the thread.
Reply to this email directly, view it on GitHub
https://github.com/mne-too

--- Comment 5 by agramfort ---
would it be possible to compare this PR with this toolbox:

https://sourceforge.net/projects/aespa/files/latest/download

in terms of result and running time?


--- Comment 6 by choldgraf ---
Does anybody here have experience with using this toolbox in matlab? I've already put way too much time on this PR and it'll be a while before I can do a full comparison between python / matlab code etc. If folks want to have a conversation about drawing inspiration from the mTRF toolbox, I'm down to do that. 


--- Comment 7 by larsoner ---
@rkmaddox does your code do the same things as [AESPA from Lalor's lab](https://sourceforge.net/projects/aespa/files/latest/download)?


--- Comment 8 by rkmaddox ---
It intends to. For the basic TRF calculation it should return the same result (when I first coded it I confirmed that it did within numerical precision, but I have not confirmed this for a couple years). The Lalor lab code does more things, I believe. My code will run significantly faster and use far less memory for the things they both do.


--- Comment 9 by choldgraf ---
I'm worried this is undergoing PR rot. We have rehashed this conversation many times but it seems like there is still much disagreement both about the API and what would happen under the hood. To me these are dissociable problems (e.g. we can make a receptive field API now and then support multiple algorithms UTH via PRs in the future). 

Following the old adage "premature optimization is the root of all evil", I think we should decide soon to either:

1. have a conversation to solidify the API and get this merged, with the goal of optimizing the algorithm etc later (assuming the inputs would be similar regardless of the backend algo)
2. Do 1, and then compare algorithms to do this under the hood
3. cut losses on this PR entirely and table this for some moment in the future

What do people think?

--- Comment 10 by agramfort ---
sorry I don't have the bandwidth to look

if you want to make this publicly available quickly I would put this in
sandbox
and it's one of the first thing we'll tackle in march during the sprint.

sounds ok to you?


--- Comment 11 by choldgraf ---
To me it's not super high-priority to have out there ASAP. I was going to incorporate the MNE code into a tutorial-style paper I'm writing but it's way past the time where that would have been possible anyway. I'm mostly trying to figure out whether I should treat this PR as a sunk cost and forget about it. I guess we can hold off until March tho

--- Comment 12 by kingjr ---
sounds like a good option to me.

On 12 December 2016 at 18:02, Chris Holdgraf <notifications@github.com>
wrote:

> To me it's not super high-priority to have out there ASAP. I was going to
> incorporate the MNE code into a tutorial-style paper I'm writing but it's
> way past the time where that would have been possible anyway. I'm mostly
> trying to figure out whether I should treat this PR as a sunk cost and
> forget about it. I guess we can hold off until March tho
>
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub
> <https://github.com/mne-tools/mne-python/pull/3728#issuecomment-266581647>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/AEp7DIEGLKHHHbAncCVdgHRrCwZykvYWks5rHdKVgaJpZM4KokeM>
> .
>


--- Comment 13 by choldgraf ---
@kingjr wait until march or just forget about this PR entirely?

--- Comment 14 by kingjr ---
Make this as one of the deliverables of the sprint, it'll be a good time for Alex, Eric and I looking at it.

(I'm actually playing with your/jona's code ATM, but I had to break it down to fit my needs, I'll keep you posted as it stabilizes)

--- Comment 15 by choldgraf ---
sounds good
-- 

On Mon, Dec 12, 2016 at 3:14 PM Jean-Rémi KING <notifications@github.com>
wrote:

> Make this as one of the deliverables of the sprint, it'll be a good time
> for Alex, Eric and I looking at it.
>
> (I'm actually playing with your/jona's code ATM, but I had to break it
> down to fit my needs, I'll keep you posted as it stabilizes)
>
> —
> You are receiving this because you authored the thread.
> Reply to this email directly, view it on GitHub
> <https://github.com/mne-tools/mne-python/pull/3728#issuecomment-266584341>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/ABwSHZQHRbpIKg41s8GH-K-eq5YWeWhHks5rHdVzgaJpZM4KokeM>
> .
>


--- Comment 16 by larsoner ---
Yeah this has been in my to-do list for a long time. Sorry it has taken so long :(

--- Comment 17 by larsoner ---
This looks 1) fairly simple (in a good way) and 2) has a pretty clean API that is 3) sklearn-consistent AFAICT.

I agree with the "premature optimization" mantra in general, but for some receptive-field use cases they are necessary for the code to even run. *Fortunately* I think we can probably work efficiency in later as a special case for this one class, or as a different class if we absolutely have to (which would be an annoying acceptable outcome to me).

@kingjr you are planning to use this a bit in the coming month or so, yes? If so my vote is to leave this PR open pending this usability feedback, and aim to merge before the sprint if @kingjr is satisfied, otherwise get to it at the sprint.

@choldgraf you're going to the sprint, yes? I certainly owe you some :beers: or :plate_with_cutlery: for dragging my feet on this one...

In the meantime if you are bored and want to update, I'll piggyback on some of @kingjr's feedback.

--- Comment 18 by larsoner ---
Okay I made some comments. @choldgraf if you want I can make a PR into your branch with some of the changes at some point (probably Jan)

--- Comment 19 by larsoner ---
I had a chat with @rkmaddox today and he likes the idea of a sklearn-like API even if his (potentially very) specific use case prevents him from using it. I think at the sprint I can work on implementing (a) fast cross-correlation method(s) and other speedups that could be used under the hood by this class and by him.

--- Comment 20 by choldgraf ---
Cool - I'll iterate on comments tomorrow and see how people feel about the PR then. I agree that we could get the API somewhat nailed down and worry about the guts later on.

--- END ---