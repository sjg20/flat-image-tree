# SPDX-License-Identifier: GPL-2.0+

"""This is the schema. It is a hierarchical set of nodes and properties, just
like the device tree. If an object subclasses NodeDesc then it is a node,
possibly with properties and subnodes.

In this way it is possible to describe the schema in a fairly natural,
hierarchical way.
"""

from elements import NodeDesc, NodeConfig, NodeImage
from elements import PropDesc, PropString, PropStringList
from elements import PropInt, PropTimestamp, PropAddressCells, PropBool

SCHEMA = NodeDesc('/', True, [
    PropTimestamp('timestamp', True),
    PropString('description', True),
    PropAddressCells(True),
    NodeDesc('images', True, [
        NodeImage(r'image-(\d)+', elements=[
            PropString('description', True),
            PropTimestamp('timestamp'),
            PropString('arch', True),
            PropString('type', True),
            PropString('compression'),
            PropInt('data-offset', True, conditional_props={'data': False}),
            PropInt('data-size', True, conditional_props={'data': False}),
            PropDesc('data', True,
                     conditional_props={'data-offset': False,
                                        'data-size': False}),
            PropString('os', True),
            PropInt('load'),
            PropString('project', True),
            PropStringList('capabilities', True),
            PropString('producer'),
            PropInt('uncomp-size'),
            PropInt('entry-start', False),
            PropInt('entry', False),
            PropInt('reloc-start', False),
        ]),
    ]),
    NodeDesc('configurations', True, [
        PropString('default'),
        NodeConfig(r'config-(\d)+', elements=[
            PropString('description', True),
            PropString('firmware', True),
            PropString('fdt'),  # Add
            PropStringList('loadables'),
            PropStringList('compatible'),
            PropBool('require-fit'),
        ]),
    ]),
])
