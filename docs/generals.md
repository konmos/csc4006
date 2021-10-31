# Byzantine Generals and the Relationship Between Software and Story

This document is a brief analysis and summary of findings, observations and anything relevant relating to the implementation of the Byzantine Generals problem based on an extracted excerpt from the presented "story" as a software specification.

## Extracted Story

The Byzantine Generals paper is primarily an engineering research paper, however, it uses a story about the Byzantine General army as an abstraction to help illustrate the problems and concepts that the paper tries to then solve. The first step of our study was extracting the story from the engineering so we could use it as a software specification. The initial extracted excerpt is the one that follows:

> Several divisions of the Byzantine army are camped outside an enemy city, each division commanded by its own general. Each general observes the enemy and communicates his observation to the others. Each general then combines all the reported observations into a single plan of action (i.e., “attack” or “retreat”), for example, by using a majority vote. Communicating only by messengers, the generals must agree upon a common, and reasonable battle plan, however, one or more of them may be traitors who will try to confuse the others. All loyal generals must carry out the same plan, whereas the traitors may do anything they wish.

One of the challenges in extracting the above excerpt was that, in the original paper, there is very little distinction between what is story and what is engineering. The presented story of the Byzantine Generals is nicely separated from the rest for about the first 2 pages, after which the line becomes blurred. It is, therefore, important to note that the above story is actually a paraphrased version of the abstraction provided in the paper. It contains some of the assumptions from the engineering and is slighlty rephrased to be easier parsed as an actual story. Namely, the following details were originally a part of the engineering:

* *attack” or “retreat”*
* *using a majority vote*

This may not seem significant, however, as we'll see later, these small details can have big impacts on the resulting software design and any assumptions that we have to make in our code. As such, an alternative, verbatim, exceprt of the story was extracted which is what the rest of the study was focused on.

## Extracted Story (verbatim)

> We imagine that several divisions of the Byzantine army are camped outside an enemy city, each division commanded by its own general. The generals can communicate with one another only by messenger. After observing the enemy, they must decide upon a common plan of action. However, some of the generals may be traitors, trying to prevent the loyal generals from reaching agreement. ... All loyal generals decide upon the same plan of action... but the traitors may do anything they wish. ... They loyal generals should not only reach agreement, but should agree upon a reasonable plan.


## User Stories

From this point onwards, we treated the above excerpt of story as our software specification and tried to implement it in code. The first step of this process was identifying any potential user stories that would best describe the problem.

* As a GENERAL I want to...
  * make observations on an enemy city to decide upon a plan of action.
  * be able to communicate with other genrals to share our observations.
* As a LOYAL GENERAL I want to...
  * decide upon a reasonable plan of action so that my division does what is best.
  * decide upon the same plan of action as all other loyal generals so order within the army is maintained.
* As a DISLOYAL GENERAL I want to...
  * make false or contradicting observations to prevent the loyal generals from reaching agreement.
* As a MESSENGER I want to...
  * deliver messages between generals/divisons so they can reach upon some agreement.

Based on this, several different implementations of the story as code were created.

# Generals 1

In `generals` (the first implementation of the story) the following classes are created to model the specification:
* General
* EnemyCity
* Messenger
* Observation (Enum)

The `EnemyCity` class is modelled to be objectively either "attackable" or not. The class is essentially a singleton that gets created at runtime.

Each `General` make observations on an instance of `EnemyCity` and can report these observations to other generals via the `Messenger`.
Generals can then each make their final decisions based on all the reported observations. They do this by simply picking whicher is most common.
It is important to note that there is no tie breaker which leads to some interesting behaviour.

### Assumptions
* There is only one messenger.
* "Enemy" and "Enemy City" are taken to refer to the same idea.
* A "reasonable plan" is assumed to mean that which wins a majority vote.
* The enemy/city is taken to have no functionality other than just "existing".
  * A city is assumed to be objectively either "attackable" or not, i.e., all generals make the same observations on the same city.
* A traitorous general simply "lies" to the other generals, i.e., he communicates the opposite of his observations to all generals.
* The observations that generals can make are either "attack" or "retreat".

### Design Decisions
* Enemy cities are simply instances of a class that essentially does nothing (yet).
* Each general works by first making an "objective" decision on an enemy. This is his true observation and not necessarily the one he communicates to the others.
* There is no tie breaker for the majority vote!

### Behaviour
In this implementation, the loyal generals **always** reach agreement. Sometimes they agree on an "unreasonable" plan. This behaviour is, effectively, the result of a number of factors, the biggest being the consistency that is introduced as a result of  every loyal general making the same observation and every traitorous general simply reporting the opposite. Thus, so long as the number of loyal generals is greater than the number of traitors, the loyal generals will agree to the same plan. If, however, there is a tie, the first observation gets returned. As the observations are stored in lists (ordered) and the generals are iterated in order (starting with the loyal generals), the first observation in the list is always that of a loyal general. Note that "tie" in this situation refers to a tie in the number of observations, i.e., the same amount of ATTACK observations as RETREAT. As for a tie in terms of the numbers of generals, the loyal generals always adopt the plan of the traitorous generals because for n loyal generals, each *loyal* general has n-1 true observations and n false observations. If there are more traitors than loyal generals, the majority wins and the loyal generals agree upon an unreasonable plan. This is because a general does not consider his own observation when making his decision (*NOTE: he probably should...*).

## Generals 1a
`generals1a` is a minor modification of `generals1` where the traitors, instead of lying, return random observations.

In this version, the majority still wins, so the behaviour is unchanged where there is no ambiguity in this regard.
Likewise, if there is a tie in the number of observations, the behaviour is the same as before. However, if there is a tie in the number of generals, it is now possible for the loyal generals to fail to reach agreement. It is also far less likely for the loyal generals to adopt an unreasonable plan now. This makes sense because if we assume that the "random" split between the observations that the traitorous generals make is 50/50, then this will have no impact on the majority.


# Generals 2

This implementation follows from the `generals1a` but makes one (small but significant) change in that each general now makes different observations on the same city. This is perhaps a more realistic view as in a real situation, if generals were camped outside an enemy city, it is likely that some would want to attack while others would prefer to retreat!

### Assumptions
* There is only one messenger.
* "Enemy" and "Enemy City" are taken to refer to the same idea.
* A "reasonable plan" is assumed to mean that which wins a majority vote.
* The enemy/city is taken to have no functionality other than just "existing".
  * Whether a city is "attackable" or not is now dependent on each general, i.e., each general cana make a different observation.
* A traitorous general makes random observations to each other general in an attmpt to confuse the loyal generals.
* The observations that generals can make are either "attack" or "retreat".

### Design Decisions
* Enemy cities are simply instances of a class that essentially does nothing (yet).
* Each general works by first making an "objective" decision on an enemy. This is his true observation and not necessarily the one he communicates to the others.
* Generals make "random" observations on a city.
* Traitorous generals randomise the decision that they communicate to others.
* There is (still) no tie breaker for the majority vote... It's not really needed here due to the randomness.
* It's probably worth mentioning that the `EnemyCity` class is now entirely useless as the logic inside `EnemyCity.should_attack` property could be moved into `General.make_observation`.


### Behaviour

As before, the majority vote wins so in cases where one observation is more popular than the other, the behaviour is unchanged. However, the problem we now have is that the loyal generals very often fail to reach an agreement due to the removed consistency and added randomness. Each loyal general makes a different observation and each traitor reports a different observation to each other general. Thus, getting all the loyal generals to agree to the same plan is an exceedingly rare occurence. Therefore, although the behaviour of this implementation might be the same as before *if* the state of the "simulation" matches, achieving that same state, even with the same parameters, is very difficult.

Another thing to note is that in this implementation the line between a loyal general and a traitorous one has become somewhat blurred in that both make initially random observations. The loyal generals simply return these first observations whereas the traitors randomise again before returning. Conceptually this mimicks the idea of the traitors simply lying about their initial observation, but logically, there is no difference. The added randomness changes nothing. This is different to the initial implementation where a city was "objectively" attackable or not. It seems the only difference here between the traitors and the loyal generals is that the loyal generals report the same observation to every general, whereas the traitors may not.

Following from this, it is interesting to note how by removing the concept of an objectively attackable city, the definition of a "false" and "true" plan (as talked about in the previous section) becomes ambigious. We have made the assumption that a "reasonable" plan is that which wins a majority vote, however, if every observation made is totally random and independednt of a city, the meaning of a majority vote gets somewhat lost.

## Generals 2a

In an attempt to "fix" some of the issues with `generals2`, this implementation simply keeps the initial randomness of the observations but reverts to the behaviour of the traitors from `generals1` where they simply "lied". This added consistency (or, "reduced randomness") makes it far less likely for the loyal generals to not reach agreement. This, however, means that the impact of the traitors is negligible if we assume that the split for observations is effectively 50/50.


# On The Quality of the Byzantine Generals Abstraction

While attempting to validate the claim that 3m+1 generals are needed to cope with m traitors, and failing to reach conclusions that agreed with the paper, I realised that the code that has been implemented thus far, based on the story presented in the research paper, is actually modelling something that is not quite the Byzantine Generals problem. The story that is presented to us as an abstraction in the first couple pages has some minor differences between the problem itself. The Byzantine Generals problem states *"a commanding general must send an order to his n-1 lieutenant generals such that...*. Interestingly, the original story has no concept of a commanding general. Furthermore, throughout the engineering part of the paper, little snippets of the "updated" story seem to appear scattered in various places. For example, at one point it is mentioned that generals should **not** report their decision to every other general (as is done in the code, based on the extracted story). Notably, the conditions for the proof in the paper seem to very subtly (but very significantly) alter the original story in various ways. This poor separation of engineering and story, and the little snippets of "story" scattered throughout and disguised as engineering result in a situation where the original abstraction of the problem becomes irrelevant and actually models something quite distinct from the problem. Perhaps the problem is that the abstraction was never meant to be used as a specification but merely a tool to help readers better visualise the Byzantine Generals problem.

## Implementation and Assumptions

In addition to the difficulties of extracting a meaningful software specification from a story, there lies the problem of implementation details and assumptions that must be made. Throughout the previous experiments, we seen that the most subtle and seemingly insignificant changes can have a big impact on the behaviour of the code. Using sets vs. lists (ordered vs. unordered), adding randomness, modelling "unnecessary" objects for the sake of staying true to the specification, etc. These are all ideas that are difficult to express in a traditional "story" but, depending, on the assumptions and implementation choices that are made you may end up implementing an entirely different system to the one seemingly proposed by the story.

# A Solution to Versioning/Maintaining Multiple Implementations

Over the course of this "study" it was unclear what the best approach to maintaining multiple implementations of the story was. As can be seen, the solution that was settled for is to simply create different Jupyter Notebooks for each "version". However, although a simple approach, it is questionable whether it is appropriate. It is not clear what constitues a new major "version" such as `generals1` vs `generals2` and what belongs in a minor version such as `generals1` vs `generals1a`. Is a major version warranted simply if the design of the code changes (as opposed to the implementation?). Moreoever, the difficulty and burden of maintaining multiple versions in several different files is a big headache, especially, when considering that there are, generally, only minor changes and most of the code is shared.


# The Value of Jupyter Notebooks

Jupyer Notebook was chosen for this problem as part of an effort to see the relationship between code and narrative, and as an avenue to explore the concept of literate programming. From this standpoint, it is unclear whether there is any value to using notebooks. One of the benefits is that it is trivial to embed documentation and things like design diagrams for each implementation, but most of the same could be achieved just as effectively with traditional code comments. This matter becomes a little more complex when you consider the previous section - if you were to, for example, remove the individual implementation notebooks and, somehow, combine them only into a single one, would it still be trivial to do so? From a practical standpoint, Jupyter Notebooks are a far cry from a real development environment. This is, of course, by design. The primary purpose of notebooks is interactive computing. It works great for visualising graphs, quickly prototyping code, or for education purposes. Working on anything more is stretching the capabilities of the system and quickly becomes counter-productive.
