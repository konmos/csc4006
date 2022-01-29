So far we have only considered the relationship between story and software in abstract terms and in practical examples. It may be helpful, however, to try and formalize this relationship based on the worked examples and background research employed so far.


# What is a story?

write about this here, settle on a definition

## Elements of a story

* Characters
* Setting
* Plot
* Conflict
* Resolution


# A formal analysis of worked examples

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
- Generals
- Messengers

setting:
- Byzantine army
- Enemy city

plot:
-

conflict:
  communication between loyal generals
  among generals which are traitorous
```

</td>
<td>

```yaml
agents:
- General
- Messenger

context:
- Generals
- Enemy city

elements:
- Observation
- Decision
- Plan
```

</td>
</tr>
</table>
