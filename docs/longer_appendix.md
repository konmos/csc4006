*This is an alternate appendix to that presented in the preliminary report, with more detail and no constraints.
The idea is that this will form at least a part of the final software report. It is written in the same style and format as the actual appendix itself, from the report.*

As part of this preliminary research we propose an experiment where we attempt to shed some light on the two questions posed at the end of section 2 *(is it helpful to think of code as stories?, to what extent can a story be used as a software specification?)*, by attempting to implement the Byzantine Generals Problem [Lamport, 1982] (BGP) in code. It is important to note that we are referring only to the story (abstraction) provided in the paper, as opposed to the problem and/or algorithm itself.

# Extracting the Story

One of the first steps (and biggest challenges) was extracting the story from the paper. It was discovered that the BGP abstraction is actually, not only a poor story, but also an inadequate representation of the problem itself. This conclusion is also arrived at in [Menon, Rainer, 2021]. As it turns out, the story we are given is poorly separated from the engineering which introduces a number of challenges, making it more difficult to deal with. Furthermore, the story itself, in a sense, gets "updated" in various places as part of the proofs and algorithms. As far as the story itself goes, it is not a very believable one for a number of reasons. Consider for example the Generals themselves - we know nothing about their motives or plans; they make for poor "characters". This immediately poses a few questions that could be asked as part of our study - namely, "what makes an *effective* story", "what is the story expressing", and "is the story telling us enough". Nonetheless, the following excerpt of story was extracted and treated as a software specification.

> We imagine that several divisions of the Byzantine army are camped outside an enemy city, each division commanded by its own general. The generals can communicate with one another only by messenger. After observing the enemy, they must decide upon a common plan of action. However, some of the generals may be traitors, trying to prevent the loyal generals from reaching agreement. ... All loyal generals decide upon the same plan of action... but the traitors may do anything they wish. ... They loyal generals should not only reach agreement, but should agree upon a reasonable plan.

It is important to note that the above extract is a verbatim one. Initially, a non-verbatim story was extracted which, we believe, would have been superior as a software specification, however, it was ultimately decided that, for this experiment, a verbatim version should be used.

# Working With the Story

We found that the story which was extracted had to undergo several transformations before ultimately becoming code, similar to how a writer uses abstractions and transforms those abstractions. For instance, the story became user stories, these then fuelled the design decisions and class diagrams, which eventually led to an implementation in Python. It is crucial to note here that at each stage, assumptions and inferences had to be made for which we can, at least in part, blame the poor initial story "specification". For instance, when drawing up the user stories for the code, inferences had to be made with regards to the motivation of the "characters". Similarly, it was unclear from the story itself what terms such as "reasonable plan" mean and how that translates into code. Perhaps this is an example of a weakness of treating stories as specifications in general and not just specific to the BGP.

Following from this, several different implementations were written, each based on a slightly different understanding of the story. As mentioned earlier, this could be one of the limitations of stories - the fact that they *can* be interpreted in different ways. Perhaps this just means that we need a more rigid set of rules for constructing effective stories such as the axioms presented by Menon et al. [Menon, Rainer, 2021].

Each one of the implementations differed only slightly from the others. A brief summary of the implementations is described:

1. Cities are objectively "attackable" or not; loyal generals return their true observation; traitors simple return the opposite
2. As in (1) but traitors now return random observations
3. As in (2) but cities are no longer modelled to be objectively "attackable", i.e., each general can make different observations on the same city.
4. As in (3) but traitors now behave as in (1)

Though the differences between each implementation are quite minor, it was noticed that each produced vastly different results. For instance, in some implementations the loyal generals ALWAYS agreed on a "reasonable" plan, while in others, they failed to do so consistently.

In an attempt to explore the concept of literate programming, Jupyter Notebooks were used for each implementation. This lead to some of the issues that were raised in the previous section - namely its cumbersome nature, especially for larger projects or projects that don't necessarily "need" extensive documentation. The value of Jupyter Notebooks, or literate programming, as part of this study is unclear.

# Existing Solutions

There exist implementations to the Byzantine Generals Problem online, such as the Python implementation by John Verwolf [https://github.com/JVerwolf/byzantine_generals]. Interestingly, many of these solutions share many similarities to the code that was written as part of this experiment, however, they are fundamentally different in the respect that they implement the actual algorithm described in the paper. While, in our implementation, the focus was on the story that was given in the paper, by treating it as a software specification, these other implementations ignore the story and implement the engineering and proofs that are laid out in the paper. The code produced from this approach is perfect in that it agrees with the paper in every respect, while the alternative approach of using the story as specification is fundamentally flawed due to the inadequacy of the story and its openness to interpretation.

# Summary

In conclusion, it was found that, due to the poor original story, the Python implementations modelled something which was not quite the Byzantine Generals Problem. This is not an entirely unsatisfying conclusion, however, as it highlights some issues and gaps in the area that must be addressed and presents us with questions that need answering. The answer to these questions may indeed bring to light the deeper relationship between story and software.
