# SPDX-License-Identifier: GPL-2.0+

"""This is the schema. It is a hierarchical set of nodes and properties, just
like the device tree. If an object subclasses NodeDesc then it is a node,
possibly with properties and subnodes.

In this way it is possible to describe the schema in a fairly natural,
hierarchical way.
"""

import copy

from elements import NodeAny, NodeDesc, NodeConfig, NodeImage
from elements import PropCustom, PropDesc, PropString, PropStringList
from elements import PropPhandleTarget, PropPhandle, CheckPhandleTarget
from elements import PropAny, PropInt, PropTimestamp, PropAddressCells, PropBool

# Known directories for installation
CRAS_CONFIG_DIR = '/etc/cras'
UCM_CONFIG_DIR = '/usr/share/alsa/ucm'
LIB_FIRMWARE = '/lib/firmware'

# Basic firmware schema, which is augmented depending on the situation.
FW_COND = {'shares': False, '../whitelabel': False}

'''
BASE_FIRMWARE_SCHEMA = [
    PropString('bcs-overlay', True, 'overlay-.*', FW_COND),
    PropString('ec-image', False, r'bcs://.*\.tbz2', FW_COND),
    PropString('main-image', False, r'bcs://.*\.tbz2', FW_COND),
    PropString('main-rw-image', False, r'bcs://.*\.tbz2', FW_COND),
    PropString('pd-image', False, r'bcs://.*\.tbz2', FW_COND),
    PropStringList('extra', False,
                   r'(\${(FILESDIR|SYSROOT)}/[a-z/]+)|' +
                   r'(bcs://[A-Za-z0-9\.]+\.tbz2)', FW_COND),
    ]

# Firmware build targets schema, defined here since it is used in a few places.
BUILD_TARGETS_SCHEMA = NodeDesc('build-targets', True, elements=[
    PropString('coreboot', True),
    PropString('ec', True),
    PropString('depthcharge', True),
    PropString('libpayload', True),
    PropString('cr50'),
], conditional_props={'shares': False, '../whitelabel': False})

BASE_AUDIO_SCHEMA = [
    PropString('card', True, '', {'audio-type': False}),
    PropFile('volume', True, '', {'audio-type': False}, CRAS_CONFIG_DIR),
    PropFile('dsp-ini', True, '', {'audio-type': False}, CRAS_CONFIG_DIR),
    PropFile('hifi-conf', True, '', {'audio-type': False}, UCM_CONFIG_DIR),
    PropFile('alsa-conf', True, '', {'audio-type': False}, UCM_CONFIG_DIR),
    PropString('topology-name', False, r'\w+'),
    PropFile('topology-bin', False, '', {'audio-type': False}, LIB_FIRMWARE),

    # TODO(sjg@chromium.org): There is no validation that we have these two.
    # They must both exist either in the model's audio node or here.
    PropFile('cras-config-dir', False, r'[\w${}]+', target_dir=CRAS_CONFIG_DIR),
    PropString('ucm-suffix', False, r'[\w${}]+'),
]

BASE_AUDIO_NODE = [
    NodeAny(r'main', [
        PropPhandle('audio-type', '/chromeos/family/audio/ANY',
                    False),
    ] + BASE_AUDIO_SCHEMA)
]

NOT_WL = {'whitelabel': False}
'''

@staticmethod
def ValidateSkuMap(val, prop):
    it = iter(prop.value)
    sku_set = set()
    for sku, phandle in itertools.izip(it, it):
        sku_id = fdt_util.fdt32_to_cpu(sku)
        if sku_id > 255:
            val.Fail(prop.node.path, 'sku_id %d out of range' % sku_id)
        if sku_id in sku_set:
            val.Fail(prop.node.path, 'Duplicate sku_id %d' % sku_id)
        sku_set.add(sku_id)
        phandle_val = fdt_util.fdt32_to_cpu(phandle)
        target = prop.fdt.LookupPhandle(phandle_val)
        if (not CheckPhandleTarget(val, target, '/chromeos/models/MODEL') and
            not CheckPhandleTarget(val, target,
                                   '/chromeos/models/MODEL/submodels/SUBMODEL')):
            val.Fail(prop.node.path,
                   "Phandle '%s' sku-id %d must target a model or submodel'" %
                   (prop.name, sku_id))


'''
NodeDesc('audio', elements=[
    NodeAny('', [PropPhandleTarget()] +
            copy.deepcopy(BASE_AUDIO_SCHEMA)),
]),
NodeDesc('firmware', elements=[
    PropString('script', True, r'updater4\.sh'),
    NodeModel([
        PropPhandleTarget(),
        copy.deepcopy(BUILD_TARGETS_SCHEMA),
        ] + copy.deepcopy(BASE_FIRMWARE_SCHEMA))
]),
NodeDesc('touch', False, [
    NodeAny('', [
        PropPhandleTarget(),
        PropString('firmware-bin', True, ''),
        PropString('firmware-symlink', True, ''),
        PropString('vendor', True, ''),
    ]),
]),
NodeDesc('mapping', False, [
    NodeAny(r'sku-map(@[0-9])?', [
        PropString('platform-name', False, ''),
        PropString('smbios-name-match', False, ''),
        PropPhandle('single-sku', '/chromeos/models/MODEL', False),
        PropCustom('simple-sku-map', ValidateSkuMap, False),
    ]),
]),

        NodeDesc('models', True, [
            NodeModel([
                PropPhandleTarget(),
                PropPhandle('default', '/chromeos/models/MODEL', False),
                PropPhandle('whitelabel', '/chromeos/models/MODEL', False),
                NodeDesc('firmware', False, [
                    PropPhandle('shares', '/chromeos/family/firmware/MODEL',
                                False, {'../whitelabel': False}),
                    PropString(('sig-id-in-customization-id'),
                               conditional_props={'../whitelabel': False}),
                    PropString('key-id', False, '[A-Z][A-Z0-9]+'),
                    copy.deepcopy(BUILD_TARGETS_SCHEMA)
                    ] + copy.deepcopy(BASE_FIRMWARE_SCHEMA)),
                PropString('brand-code', False, '[A-Z]{4}'),
                PropString('powerd-prefs', conditional_props=NOT_WL),
                PropString('wallpaper', False, '[a-z_]+'),
                NodeDesc('audio', False, copy.deepcopy(BASE_AUDIO_NODE),
                         conditional_props=NOT_WL),
                NodeDesc('submodels', False, [
                    NodeSubmodel([
                        PropPhandleTarget(),
                        NodeDesc('audio', False, copy.deepcopy(BASE_AUDIO_NODE),
                                 conditional_props={'../../audio': False}),
                        NodeDesc('touch', False, [
                            PropString('present', False, r'yes|no|probe'),
                            PropString('probe-regex', False, ''),
                        ]),
                    ])
                ], conditional_props=NOT_WL),
                NodeDesc('thermal', False, [
                    PropFile('dptf-dv', False, r'\w+/dptf.dv',
                             target_dir='/etc/dptf'),
                ], conditional_props=NOT_WL),
                NodeDesc('touch', False, [
                    PropString('present', False, r'yes|no|probe'),
                    # We want to validate that probe-regex is only present when
                    # 'present' = 'probe', but have no way of doing this
                    # currently.
                    PropString('probe-regex', False, ''),
                    NodeAny(r'(stylus|touchpad|touchscreen)(@[0-9])?', [
                        PropString('pid', False),
                        PropString('version', True),
                        PropPhandle('touch-type', '/chromeos/family/touch/ANY',
                                    False),
                        PropString('firmware-bin', True, '',
                                   {'touch-type': False}),
                        PropString('firmware-symlink', True, '',
                                   {'touch-type': False}),
                        PropString('date-code', False),
                    ]),
                ], conditional_props=NOT_WL),
            ])
        ]),
'''

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
            PropInt('data-offset', False),
            PropInt('data-size', False),
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
