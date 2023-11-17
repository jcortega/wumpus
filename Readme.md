This is a Wumpus World game simulator.

## To run the simulator using the Move Planning Agent, use the command below:

Install required libraries in your own venv

```
python -m venv .env
source .env/bin/activate
pip install networkx matplotlib

```

## To run simulator, run main.py with below format

```
python src/main.py <agent_type>
```

`<agent_type>` could be `human`, `move_planning`, `naive` or `proba_agent`.

More examples below.

## To run the simulator using the Naive Agent, use the command below:

```
python src/main.py naive
```

A sample run is shown below.

```
(base) jerome@dev:~/wumpus$ python src/main.py naive
Running episode with naive agent...


+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|    bsA›|        |        |        |
+--------+--------+--------+--------+
Observed: {'stench': True, 'breeze': True, 'glitter': False, 'bump': False, 'scream': False, 'points': 0}
Grabbing gold ...


+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|    bsA›|        |        |        |
+--------+--------+--------+--------+
Observed: {'stench': True, 'breeze': True, 'glitter': False, 'bump': False, 'scream': False, 'points': -1}
Grabbing gold ...


+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|    bsA›|        |        |        |
+--------+--------+--------+--------+
Observed: {'stench': True, 'breeze': True, 'glitter': False, 'bump': False, 'scream': False, 'points': -1}
Forward ...


+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|    bs  |    WA› |        |        |
+--------+--------+--------+--------+
Observed: {'stench': False, 'breeze': False, 'glitter': False, 'bump': False, 'scream': False, 'points': -1001}


+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|        |        |        |        |
+--------+--------+--------+--------+
|    bs  |    WA› |        |        |
+--------+--------+--------+--------+
Agent died with -1003 points
```

You can also run the simulator in human or interactive mode by running the simulator as follows:

```
python src/main.py human
```
