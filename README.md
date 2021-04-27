# OEIS explorer

This is a tool for exploring two different kinds of relationships between sequences in the OEIS: mentions (links) of other sequences on a sequence's page, and large numbers that appear in multiple different sequences.

You can view the tool [here](http://alexmojaki.github.io/oeis-explorer) for more explanation.

You can also explore the resulting JSON data [here](https://github.com/alexmojaki/oeis-explorer/blob/master/frontend/src/result.json).

To run this code:

- [Download `full_sequences.json` here](https://drive.google.com/file/d/1bN3LrTGRenfw-esiBe4GI0CqtIfPWjlC/view?usp=sharing).
- `pip install networkx`
- `python analyse.py`

At least Python 3.6 is required.
