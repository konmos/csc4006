So far we have only considered the relationship between story and software in abstract terms and in practical examples. It may be helpful, however, to try and formalize this relationship based on the worked examples and background research employed so far.


# What is a story?

The task of defining the meaning of the word "story" is a seemingly simple one and yet we still have not arrived at a single, all-encompassing definition after all these years, since the advent of story telling dating back to ~2100BC with the Epic of Gilgamesh. Various definitions and classifications have been proposed in the past for identifying what a story is, including;

* Certain length?
* Anecdotes?
* Ideas, pictures, illustrating something?
* Cannot be summarized or reduced without sacrificing the very qualities that distinguish it.
* What has not been said?
* Nothing can be added, nothing taken away.
* Aristotelian principles?
* Single effect? One thing?
* Restricted plot and characters?
* Few protagonists?
* Consistent perspective?

These are topics that are covered in great detail by Francine Prose in her essay "What Makes a Short Story?" [Alice LaPlante, The Making of a Story, p. 167], however, as Francine identifies and expounds in her essay, none of these is entirely satisfying. It seems that no matter which definition is settled for, there is always a counter-example which diametrically opposes the chosen definition.

The most interesting of these definitions, may perhaps be that which is offered by Edgar Allan Poe and his concept of the "single effect". While, initially, it may be difficult to understand what exactly Poe is alluding to, thinking about his explanation of it alongside that offered by V.S. Pritchett and Chekov may shed some light as to what it might mean. Poe says "in the whole composition, there should be no word written, of which the tendency, direct or indirect, is not to the one pre-established design", while Pritchett and Checkov note, respectively, "The novel tends to tell us everything whereas the short story tells us only one thing", and "the result is something like the vault of heaven: one big moon and a number of very small stars around it...". To put simply, it could be said that what this "single effect" is alluding to is the "watering down" of a story. Each story, should ideally, have a single, clear-cut focus without many distractions. Of course, in practice, this is difficult to achieve and few readers could explain exactly what a "single effect" is, or what precisely is the "one thing" that our favorite story is telling us. This definition, like all the others, falls short in the general case. Despite this, we propose that this is the definition which we should settle for when restraining ourselves to the context of story within software. We believe that this concept precisely defines what makes a good story with regards to software. This becomes clear later when we look at examples where the story violates this definition to the point where a software solution is impossible to be achieved (at the very least, without simplifying and breaking up the story).

Thus, it is important to mention that from here onwards, when we say "story" we are referring strictly to "short stories", as opposed to something more substantive like a novel. The reason for this is that, quite clearly, a larger work akin to a novel would violate the definitions and constraints we propose, nor would it be a good candidate for a software specification.


# Elements of a story

Stories have long been defined as being made up a series of "essential elements". This, like all other definitions fails in the general case (as mentioned in the previous section) as counter-examples can always be found. Moreover, what these elements are varies from person to person. However, we propose that, in addition to the definition put forward in the previous section, a story (in the context of software) must be composed of at least the following elements:

* Characters
* Setting
* Plot
* Conflict
* Resolution

## What is the "Plot"?

These elements are, for the most part, quite self-explanatory. However, it may be beneficial to explain exactly what is meant by the term "plot".
The term "plot" is quite similar to the term "story" in that it seems to have many definitions and no consensus as to what the right one is. For simplicity, however, we will agree with what Karin Kukkonen says in the Handbook of Narratology (https://doi.org/10.1515/9783110316469.706);

"The term "plot" designates the ways in which the events and characters' actions in a story are arranged and how this arrangement in turn facilitates identification of their motivations and consequences... Plot therefore lies between the events of a narrative on the level of story and their presentation on the level of discourse."

What interests us here the most, as software engineers, is the fact that the plot deals with **events** and **actions**. This conclusion is quite similar to that arrived at by Sileno et al. in the paper "Legal Knowledge Conveyed by Narratives: Towards a Representational Model" in which the *story* is defined as a partially ordered set of events linked by a series of conditions. The *plot* then is said to impose a series of constraints on the ordering of these events. Although, Sileno et al. propose a good and comprehensive explanation of story and plot, we found that the line between conditions and events is not clear cut and there is some overlap between the two. From a software perspective, it is more beneficial to think of it as events and actions instead. Moreover, in the software engineering context, the strict ordering of events is not as crucial - it is not *irrelevant* but also not entirely integral to the solution.


*[https://en.wikipedia.org/wiki/Plot_(narrative)] See this for more details. Plot implies causality.*

# A formal analysis of worked examples

With the above in mind, we now propose that any story which falls into the above two definitions and is computationally representable, can be mapped directly to a suitable software implementation. In the following examples, we examine the stories and their software solutions (if any) that have been looked at thus far and break them down into the 5 basic elements mentioned previously. We do the same for the software implementation. Through this approach, we see that each story element has a near-one-to-one equivalent in the software context. We visualize this by way of a series of YAML (https://yaml.org/) "documents".

We propose that a piece of software, similar to a story, can be described by way of a series of essential elements. These are as follows;

* Agents
* Events
* Actions
* Components
* Flow

We define these elements;
* Agents - the primary actors of the software solution. This is where most of the logic and "executable" code will reside. The agents are generally derived directly from the *characters* of the story, however, this may not always be the case.
* Components - miscellaneous elements of the software solution that make up neither the agents nor context, but are nonetheless, integral to the software solution. Generally, the components are what tie the agents, context, and overarching software solution together.
* Events - these are global events that occur in a world and can trigger other events.
* Actions - actions are similar to events, however, they are not global but local to the agents. For example `dine` can be a global event whereas `Philosopher.eat` is an action.
* Flow - this describes the interaction between the events and the agents. This is done by what we refer to as FDL - Flow Description Language.

As will be clear from the following examples, these elements can be generally derived directly from the elements of the story. They may not always be, however, direct, one-to-one equivalents.

Furthermore, it is important to note that in certain circumstances certain story elements may need to be inferred. For example, it is often the case that the resolution is not explicitly given in the story but we, nonetheless, have a good idea of what it might be.

**NOTE: Currently only the DP example is up to date.**

## Byzantine Generals Problem

> We imagine that several divisions of the Byzantine army are camped outside an enemy city, each division commanded by its own general. The generals can communicate with one another only by messenger. After observing the enemy, they must decide upon a common plan of action. However, some of the generals may be traitors, trying to prevent the loyal generals from reaching agreement. ... All loyal generals decide upon the same plan of action... but the traitors may do anything they wish. ... They loyal generals should not only reach agreement, but should agree upon a reasonable plan.

<table>
<tr>
<th>Story</th>
<th>Software</th>
</tr>
<tr>
<td>

```yaml
characters:
- Loyal generals
- Traitorous generals
- Messengers

setting:
- Byzantine army
- Enemy city

plot:
- Divisions of army camped outside enemy city
- Generals communicate their observations via messenger
- Traitorous generals preventing loyal generals from
  reaching agreement

conflict:
  Communication between loyal generals
  among generals which are traitorous

resolution:
  Reliable means of communication for loyal generals
```

</td>
<td>

```yaml
agents:
- General
- Messenger

context:
- Byzantine army
- Enemy city

components:
- Observation
- Decision
- Plan
```

</td>
</tr>
</table>

Notes:
* "Observation" is a key concept in the source code
* "Decision" is whatever the generals decide upon hearing observations
* "Plan" is the final plan agreed to by the generals (if any)
* "Byzantine army" could be the list of generals that is constructed at the beginning of the program

## Dining Philosophers

> The life of a philosopher consists of an alternation of thinking and eating.
> Five philosophers, numbered from 0 through 4 are living in a house where the table laid for them, each philosopher having his own place at the table:
> Their only problem - besides those of philosophy - is that the dish served is a very difficult kind of spaghetti, that has to be eaten with two forks. There are two forks next to each plate, so that presents no difficulty: as a consequence, however, no two neighbors may be eating simultaneously.

> *The philosophers overcome this problem by signalling amongst themselves whether or not it is appropriate to eat. When a philosopher lets the others know that he is hungry, he checks to make sure that none of his neighbors are eating before picking up his forks and consuming his meal. Once he is finished, he signals to his immediate neighbors that he is no longer eating. The philosophers next to him can then follow the same procedure should they get hungry. Thus, the philosophers ensure that no two neighbors attempt to eat their meal simultaneously.*

<table>
<tr>
<th>Story</th>
<th>Software</th>
</tr>
<tr>
<td>

```yaml
characters:
- Philosophers

setting:
- Table

plot:
- Table is laid for each philosopher, with two forks next to each plate.
- Two forks are needed for a philosopher to eat.
- The philosophers alternate thinking and eating.

conflict:
  Eating spaghetti with a limited number of forks

resolution:
  A means of reliably eating the spaghetti
```

</td>
<td>

```yaml
agents:
- Philosopher

events:
- dine

actions:
- Philosopher.eat
- Philosopher.think

components:
- Fork

flow:
- dine -> {Philosopher.think}
- Philosopher.think -> {Philosopher.eat}
```

</td>
</tr>
</table>

## Hansel and Gretel

> Hansel and Gretel were scared. They knew the forest was deep and dark, and that it was easy to get lost. "Don't worry! I have a plan!" whispered Hansel to Gretel. He went to the back of the house and filled his pockets with white pebbles from the garden. Then the two children started walking, following their stepmother’s directions. Every few steps, Hansel dropped a little white pebble on the ground. ... Hansel waited until the moon was bright. The moonlight shone through the tall trees and made his tiny white pebbles glow. They followed the trail of pebbles all the way back home.

<table>
<tr>
<th>Story</th>
<th>Software</th>
</tr>
<tr>
<td>

```yaml
characters:
- Hansel
- Gretel
- Stepmother

setting:
- Forest

plot:
- H&G get lost in a forest
- Hansel finds the way back using
  pebbles he collected/dropped earlier.

conflict:
  Being lost in a forest

resolution:
  Finding your way out of the forest
```

</td>
<td>

```yaml
agents:
- Hansel

context:
- Forest

components:
- Pebble
```

</td>
</tr>
</table>

Notes:
* Here, "context" is a little tricky. There are two H&G solutions here; one which works with co-ordinates mapped to a 2d space, the other which works with node graphs. In either case, these are quite abstract concepts. They could effectively represent the "forest" in the story, thus this is what was settled for here.


## Winograd and Flores

> You have been commuting to work in your old Chevrolet. Recently you have had to jump-start it three times, and there has been an ominous scarping sound every time you apply the brakes. One morning as you are driving to work you cannot get it into first gear. You take it to a mechanic who says there is a major problem with the transmission.
>
>. . .
>
>You talk to your husband and decide that there are several alternatives – you can have the old car repaired, or you can buy a used or a new car. If you want a used car you can try to get it through friends and newspaper ads, or you can go to a dealer. If you get a new one you may want a van you can use for camping trips, but you’re not sure you can afford it and still go on the vacation you had planned. In fact you’re not sure you can afford a new car at all, since you have to keep up the payments and insurance on your husband’s car as well.
>
>. . .
>
>on the next day (since you can’t drive to work) you call and check the city buses and fnd one you can take. After a few days of taking the bus you realize you didn’t really need the car...
>
>. . .
>
>[after a few days of commuting on the bus, you realise that the] bus ride takes too long, and you are complaining about the situation to your friend at work. He commiserates with you, since his bicycling to work is unpleasant when it rains. The two of you come up with the idea of having the company buy a van for an employee car pool.
>
>. . .
>
>[later, you] talk to another friend who has just gotten his car back from the shop. He hears your story and expresses surprise at the whole thing. It never occurred to him to do anything except have it fixed, just as he always did.

<table>
<tr>
<th>Story</th>
<th>Software</th>
</tr>
<tr>
<td>

```yaml
characters:
- "Me" ("Protagonist?")
- Husband
- Mechanic
- Friend 1
- Friend 2

setting:
- Work
- Mechanic
- Home
- Bus

plot:
- Car broke down
- Searching for an alternative means of transport

conflict:
  No means of transport for commuting and/or travel

resolution:
```

</td>
<td>

```yaml
agents:
context:
components:
```

</td>
</tr>
</table>


## Baby Shoes

> "For sale. Baby's shoes. Never worn."

<table>
<tr>
<th>Story</th>
<th>Software</th>
</tr>
<tr>
<td>

```yaml
characters:
- Seller
- Buyer

setting:

plot:
- Shoes for sale

conflict:
  Wanting to sell shoes

resolution:
  Selling the shoes
```

</td>
<td>

```yaml
agents:
context:
components:
```

</td>
</tr>
</table>

## Pierson v. Post

>Post was hunting a fox with a horse and hounds in a wild and uninhabited land, and was about to catch it, but Pierson, although conscious of Post’s pursuit, intercepted, killed and took the animal.
>
>Both claimed the fox, the first appeal had found for Post, but this court reverted the previous result. The different positions are expressed by two judges: Tompkins (majority) and Livingston (dissent).
>
>The first, supported by classical jurisprudence, claims that possession of a fera naturae, where fera naturae is an animal wild by nature, occurs only if there is occupancy, i.e. taking physical possession. Pierson took the animal, so he owns it.
>
>The second argues that if someone starts and hunts a fox with hounds in a vast and uninhabited land has a right of taking the fox on any other person who saw he was pursuing it.

<table>
<tr>
<th>Story</th>
<th>Software</th>
</tr>
<tr>
<td>

```yaml
characters:
- Post
- Pierson
- Fox
- Tompkins
- Livingston

setting:
- Wild, uninhabited land
- Court

plot:
- Post hunts for fox
- Pierson catches the fox instead
- Dispute over who "owns" the fox

conflict:
  Who does the fox belong to?

resolution:
```

</td>
<td>

```yaml
agents:
context:
components:
```

</td>
</tr>
</table>


# TODO / Further Work

* Complete the other examples.
* Potential visualization improvements.
  * Node colors, sizes, weights, relationships, etc...
  * Display agents/components.
  * Agent/component interactions.
* Threading support.
* Live stepping through events.
* Web interface (?)
* Command line interface.
* More examples/more complex example.
* More configurability (?)
* Figure out components (maybe they need removed?)
