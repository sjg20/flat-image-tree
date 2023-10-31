# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Schema elements

This module provides schema elements that can be used to build up a schema for
validation of a devicetree.
"""

import re

from dtoc.fdt import Type
from dtoc import fdt_util

def check_phandle_target(val, target, target_path_match):
    """Check that the target of a phandle matches a pattern

    Args:
        val: Validator (used for model list, etc.)
        target: Target node path (string)
        target_path_match: Match string. This is the full path to the node that
            the target must point to. Some 'wildcard' nodes are supported in the
            path:

                MODEL - matches any model node
                SUBMODEL - matches any submodel when MODEL is earlier in the
                    path
                ANY - matches any node

    Returns:
        True if the target matches, False if not
    """
    model = None
    parts = target_path_match.split('/')
    target_parts = target.path.split('/')
    valid = len(parts) == len(target_parts)
    if valid:
        for i, part in enumerate(parts):
            if part == 'MODEL':
                if target_parts[i] in val.model_list:
                    model = target_parts[i]
                    continue
            if part == 'SUBMODEL' and model:
                if target_parts[i] in val.submodel_list[model]:
                    continue
            elif part == 'ANY':
                continue
            if part != target_parts[i]:
                valid = False
    return valid


# pylint: disable=R0903
class SchemaElement():
    """A schema element, either a property or a subnode

    Args:
        name: Name of schema eleent
        prop_type: String describing this property type
        required: True if this element is mandatory, False if optional
        conditional_props: Properties which control whether this element is
            present. Dict:
                key: name of controlling property
                value: True if the property must be present, False if it must be
                    absent
    """
    def __init__(self, name, prop_type, required=False, conditional_props=None):
        self.name = name
        self.prop_type = prop_type
        self.required = required
        self.conditional_props = conditional_props
        self.parent = None

    def validate(self, val, prop):
        """Validate the schema element against the given property.

        This method is overridden by subclasses. It should call val.fail() if
        there is a problem during validation.

        Args:
            val: FdtValidator object
            prop: Prop object of the property
        """


class PropDesc(SchemaElement):
    """A generic property schema element (base class for properties)"""


class PropString(PropDesc):
    """A string-property

    Args:
        str_pattern: Regex to use to validate the string
    """
    def __init__(self, name, required=False, str_pattern='',
                             conditional_props=None):
        super().__init__(name, 'string', required, conditional_props)
        self.str_pattern = str_pattern

    def validate(self, val, prop):
        """Check the string with a regex"""
        if not self.str_pattern:
            return
        pattern = '^' + self.str_pattern + '$'
        val_m = re.match(pattern, prop.value)
        if not val_m:
            val.fail(
                prop.node.path,
                f"'{prop.name}' value '{prop.value}' does not match pattern '{pattern}'")


class PropInt(PropDesc):
    """Single-cell (32-bit) integer"""
    def __init__(self, name, required=False, conditional_props=None):
        super().__init__(name, 'int', required, conditional_props)

    def validate(self, val, prop):
        """Check the timestamp"""
        if prop.type != Type.INT:
            val.fail(
                prop.node.path,
                f"'{prop.name}' value '{prop.value}' must be a u32")


class PropTimestamp(PropInt):
    """A timestamp in u32 format"""


class PropAddressCells(PropDesc):
    """An #address-cells property"""
    def __init__(self, required=False, conditional_props=None):
        super().__init__('#address-cells', 'address-cells', required,
                         conditional_props)

    def validate(self, val, prop):
        """Check the timestamp"""
        if prop.type != Type.INT:
            val.fail(
                prop._node.path,
                f"'{prop.name}' value '{prop.value}' must be a u32")
        val = fdt_util.fdt32_to_cpu(prop.value)
        if val not in [1, 2]:
            val.fail(prop._node.path,
                     f"'{prop.name}' value '{val}' must be 1 or 2")


class PropBool(PropDesc):
    """Boolean property"""
    def __init__(self, name, required=False, conditional_props=None):
        super().__init__(name, 'bool', required, conditional_props)


class PropStringList(PropDesc):
    """A string-list property schema element

    Note that the list may be empty in which case no validation is performed.

    Args:
        str_pattern: Regex to use to validate the string
    """
    def __init__(self, name, required=False, str_pattern='',
                             conditional_props=None):
        super().__init__(name, 'stringlist', required, conditional_props)
        self.str_pattern = str_pattern

    def alidate(self, val, prop):
        """Check each item of the list with a regex"""
        if not self.str_pattern:
            return
        pattern = '^' + self.str_pattern + '$'
        for item in prop.value:
            m_str = re.match(pattern, item)
            if not m_str:
                val.fail(
                    prop.node.path,
                    f"'{prop.name}' value '{item}' does not match pattern '{pattern}'")


class PropPhandleTarget(PropDesc):
    """A phandle-target property schema element

    A phandle target can be pointed to by another node using a phandle property.
    """
    def __init__(self, required=False, conditional_props=None):
        super().__init__('phandle', 'phandle-target', required,
                         conditional_props)


class PropPhandle(PropDesc):
    """A phandle property schema element

    Phandle properties point to other nodes, and allow linking from one node to
    another.

    Properties:
        target_path_match: String to use to validate the target of this phandle.
                It is the full path to the node that it must point to. See
                check_phandle_target for details.
    """
    def __init__(self, name, target_path_match, required=False,
                             conditional_props=None):
        super().__init__(name, 'phandle', required, conditional_props)
        self.target_path_match = target_path_match

    def validate(self, val, prop):
        """Check that this phandle points to the correct place"""
        phandle = prop.GetPhandle()
        target = prop.fdt.LookupPhandle(phandle)
        if not check_phandle_target(val, target, self.target_path_match):
            val.fail(
                prop.node.path,
                f"Phandle '{prop.name}' targets node '{target.path}' which does not "
                f"match pattern '{self.target_path_match}'")


class PropCustom(PropDesc):
    """A custom property with its own validator

    Properties:
        validator: Function to call to validate this property
    """
    def __init__(self, name, validator, required=False, conditional_props=None):
        super().__init__(name, 'custom', required, conditional_props)
        self.validator = validator

    def validate(self, val, prop):
        """Validator for this property

        This should be a static method in FdtValidator.

        Args:
            val: FdtValidator object
            prop: Prop object of the property
        """
        self.validator(val, prop)


class PropAny(PropDesc):
    """A placeholder for any property name

    Properties:
        validator: Function to call to validate this property
    """
    def __init__(self, validator=None):
        super().__init__('ANY', 'any')
        self.validator = validator

    def validate(self, val, prop):
        """Validator for this property

        This should be a static method in FdtValidator.

        Args:
            val: FdtValidator object
            prop: Prop object of the property
        """
        if self.validator:
            self.validator(val, prop)


class PropOneOf(PropDesc):
    """Allows selecting one of a variety of options

    Properties:
        validator: Function to call to validate this property
    """
    def __init__(self, name, required=False, options=None,
                 conditional_props=None):
        super().__init__(name, 'oneof', required, conditional_props)
        self.options = options or []

    def validate(self, val, prop):
        """Validator for this property

        This should be a static method in FdtValidator.

        Args:
            val: FdtValidator object
            prop: Prop object of the property
        """
        # TODO


class NodeDesc(SchemaElement):
    """A generic node schema element (base class for nodes)"""
    def __init__(self, name, required=False, elements=None,
                             conditional_props=None):
        super().__init__(name, 'node', required, conditional_props)
        self.elements = elements
        for element in elements:
            element.parent = self

    def get_nodes(self):
        """Get a list of schema elements which are nodes

        Returns:
            List of objects, each of which has NodeDesc as a base class
        """
        return [n for n in self.elements if isinstance(n, NodeDesc)]


class NodeModel(NodeDesc):
    """A generic node schema element (base class for nodes)"""
    def __init__(self, elements):
        super().__init__('MODEL', elements=elements)


class NodeSubmodel(NodeDesc):
    """A generic node schema element (base class for nodes)"""
    def __init__(self, elements):
        super().__init__('SUBMODEL', elements=elements)


class NodeAny(NodeDesc):
    """A generic node schema element (base class for nodes)"""
    def __init__(self, name_pattern, elements):
        super().__init__('ANY', elements=elements)
        self.name_pattern = name_pattern

    def validate(self, val, node):
        """Check the name with a regex"""
        if not self.name_pattern:
            return
        pattern = '^' + self.name_pattern + '$'
        m_name = re.match(pattern, node.name)
        if not m_name:
            val.fail(
                node.path,
                f"Node name '{node.name}' does not match pattern '{pattern}'")


class NodeImage(NodeAny):
    """A FIT image node"""
    def __init__(self, name_pattern, elements):
        super().__init__(name_pattern=name_pattern, elements=elements)


class NodeConfig(NodeAny):
    """A FIT config node"""
    def __init__(self, name_pattern, elements):
        super().__init__(name_pattern=name_pattern, elements=elements)
