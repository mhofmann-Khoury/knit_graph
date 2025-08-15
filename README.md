# knit_graphs

[![PyPI - Version](https://img.shields.io/pypi/v/knit-graphs.svg)](https://pypi.org/project/knit-graphs)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/knit-graphs.svg)](https://pypi.org/project/knit-graphs)

-----
## Description
The knit-graphs packaged provides a data structure for representing knitted structures formed of loops of yarn (nodes) connected by various edge structures. Loops are connected by: floats (yarn-edges) in a yarn graph structure, stitch edges (loops pulled through loops), and crossed over each other in a wale-braid structure.

Knit graphs provide a powerful tool for representing knitted structures for digital fabrication systems such as knitting machine programming languages and design tools.

Additional details about this knit-graph construction are available in the ACM publication:
["KnitPicking Texture: Programming and Modifying Complex Knitted Textures for Machine and Hand Knitting"](https://doi.org/10.1145/3332165.3347886)

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Knit Graph Generators](#knit-graph-generators)
  - [Visualizing Knit Graphs](#visualizing-knit-graphs)
- [Credits](#credits)
- [License](#license)



## Installation

```console
pip install knit-graphs
```

## Usage

### Knit Graph Generators
The [knit-graph-generators subpackage](https://github.com/mhofmann-Khoury/knit_graph/tree/main/src/knit_graphs/knit_graph_generators) provides a library of basic knit graphs to generate such as casting on loops of a knitted structure, creating Jersey (aka Stockinette) tubes and swatches, and other basic textures.
For example, to generate a swatch of knit-purl ribbing use the following:

```python
from knit_graphs.basic_knit_graph_generators import kp_rib_swatch

width = 10
height = 10
kp_rib_swatch = kp_rib_swatch(width, height)
```
Additional examples of knitgraph generator usage can be found in the [Knit_Graph test module](https://github.com/mhofmann-Khoury/knit_graph/blob/main/tests/test_Knit_Graph.py).

Knitgraphs can be created without generators. We encourage users to review the generators as simple examples on creating a knit graph programmatically.

### Visualizing Knit Graphs
We provide simple support for visualizing knit graphs. This is primarily used to debugging simple knit graph programs.

For example, we can visualize a swatch of seed stitch (checkered knit and purl stitches) with the following code.

```python
from knit_graphs.basic_knit_graph_generators import seed_swatch
from knit_graphs.knit_graph_visualizer.Stitch_Visualizer import visualize_stitches

width = 4
height = 4
swatch = seed_swatch(width, height)
visualize_stitches(swatch)
```
The visualizer shows knit stitches (loops pulled from the back of the fabric to the front) as blue edges and purl stitches (loops pulled from the front to back) (aka back-knits) as red edges. Loop nodes are circles labeled with their time-ordered index and colored to match their yarn (defaults to dark green). The yarn edges (aka floats) connecting them are made of thin edges the same color as the loop nodes.

Additional examples of using the visualizer are available in the [Stitch Visualizer Tests Module](https://github.com/mhofmann-Khoury/knit_graph/blob/main/tests/test_Stitch_Visualizer.py)

## Credits
The design of this data scructure was completed by the authors of
["KnitPicking Texture: Programming and Modifying Complex Knitted Textures for Machine and Hand Knitting"](https://doi.org/10.1145/3332165.3347886).

The inclusion of the Artin-Braide wale crossing construction was inspired by ["An Artin Braid Group Representation of Knitting Machine State with Applications to Validation and Optimization of Fabrication Plans"](https://doi.org/10.1109/ICRA48506.2021.9562113) by Jenny Lin and James McCann.

## License

`knit-graphs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
