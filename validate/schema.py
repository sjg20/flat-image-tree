
"""This is the schema. It is a hierarchical set of nodes and properties, just
like the device tree. If an object subclasses NodeDesc then it is a node,
possibly with properties and subnodes.

In this way it is possible to describe the schema in a fairly natural,
hierarchical way.
"""
SCHEMA = NodeDesc('/', True, [
    NodeDesc('chromeos', True, [
        NodeDesc('family', True, [
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
                    PropCustom('simple-sku-map',
                               CrosConfigValidator.ValidateSkuMap, False),
                ]),
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
        NodeDesc('schema', False, [
            NodeDesc('target-dirs', False, [
                PropAny(),
            ])
        ])
    ])
])
