# michie

Distributed high-throughput pythonic framework for multi-agent simulations

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


## Examples

You can find some examples [here](https://github.com/galatolofederico/michie-private/tree/main/examples)

## Contributions and license

The code is distributed as Free Software under the [GNU/GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license.
It is not only possible, but also encouraged, to copy, adapt, and republish it.

If you have any further questions, please contact me at [federico.galatolo@ing.unipi.it](mailto:federico.galatolo@ing.unipi.it) or on Telegram [@galatolo](https://t.me/galatolo). 