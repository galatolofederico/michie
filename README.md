# michie

Distributed high-throughput pythonic framework for multi-agent simulations

![](./README.md.d/michie-architecture.png) 


## Installation

`michie` is available on PyPI. To install it

```
pip install michie
```

## Usage

In `michie` each object has its own **state** and there is one **global state**

There are **three** distinct types of operations in `michie`:

- **GlobalStateMappers**
    -  Can **read** and **write** **every state**
    -  Can **read** and **wite** the **global state**
    -  Are executed **synchronously** from the *Master process*
- **StateMappers**
    - Can **read** and **write** **one state**
    - Can **only read** the **global state**
    - Are executed **asynchronously** from the *Worker processes*
- **Transitions**
    - Can **read** and **write** **one state**
    - **Cannot read** the **global state**
    - Are executed **asynchronously** from the *Worker processes*


## Distributed Model

`michie` executes `Transitions` and `StateMappers` on remote *Workers*.
It uses the fastest JSON python serializer [orjson](https://github.com/ijl/orjson) to serialize jobs and results.
Before sending the job to the workers it runs the `requirements` function to check if all the needed fields are available in the current state and uses the `state_map` and `global_state_map` (only for `StateMappers`) to map the whole state in a smaller `mapped_state` to be serialized (reducing the communication overhead to the minimum)

![](./README.md.d/michie-execution.png)

## Examples

You can find some examples [here](https://github.com/galatolofederico/michie-private/tree/main/examples)

## Contributions and license

The code is distributed as Free Software under the [GNU/GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license.
It is not only possible, but also encouraged, to copy, adapt, and republish it.

If you have any further questions, please contact me at [federico.galatolo@ing.unipi.it](mailto:federico.galatolo@ing.unipi.it) or on Telegram [@galatolo](https://t.me/galatolo). 