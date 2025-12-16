# Day 08 – Pokémon – data catch 'em all

In this mini-project we use a Pokémon dataset (Gen 1–9) to **argue, in a very scientific and totally unbiased way**, that early generations were better.

Spoiler: we make a **case** that the old gens are better because:
1. They’re more *balanced* — lower average total stats and smaller standard deviations, meaning fewer absurd power spikes.
2. They make more sense narratively — fewer “special” Pokémon and a stronger presence of classic, down-to-earth types.
3. Their type ecosystems show cleaner structure.

We load the Pokémon dataset, compute derived statistics, and visualize how stats, type diversity, and magical flavor change across generations.

## What we analyze

### 1. Total stats per generation
We compute each Pokémon's combined battle stats and inspect the mean and standard deviation of total stats by generation. The trend lines show clear increases over the years, suggesting that later generations introduce progressively stronger Pokémon, gradually shifting the balance of the ecosystem and reducing the emphasis on more modest, well-rounded designs.


### 2. Legendary + Mythical “specialness” ratio
How many Pokémon are *truly special* each generation?
If every new region throws in 15 legendaries, the word “legendary” starts losing meaning.

### 3. Shannon entropy of Pokémon types
We compute type entropy to quantify how diverse each generation's ecosystem is.
More entropy, more varied types.
Less entropy, tighter, more focused design.

### 4. Magical vs. Regular types
We group types into:
- **Magical** (Fire, Electric, Fairy, Psychic, Ghost and Dragon)
- **Regular** (everyone else)

Then we track the magical/regular ratio across generations.
If the games drift from “creatures in a fantasy world” to “sparkly demigods everywhere” this is where it shows.

---

## Conclusion

Using nothing but hard data, objective analysis, and a healthy dose of nostalgia:
- Early generations appear statistically more grounded.
- Later generations show increased magical saturation, more special Pokémon, and a rise in overall power levels.
- Whether that’s good or bad… well, that’s what the graphs are for.
