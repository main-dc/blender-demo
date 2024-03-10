# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Autoflow: Automatically remesh objects in Blender using QuadriFlow.
#  Copyright (C) 2024 Davin C. (davin.github@protonmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

"""Autoflow add-on for Blender.

This add-on automatically remeshes objects using QuadriFlow.
Instructions for add-on installation can be found online here:
https://docs.blender.org/manual/en/latest/editors/preferences/addons.html
"""

bl_info = {
    "name": "Autoflow",
    "description": "Automatically remesh objects using QuadriFlow.",
    "author": "Davin C. (davin.github@protonmail.com)",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "location": "View 3D > Tool Shelf > Tools > Autoflow",
    "warning": "",
    "category": "Mesh",
}

# Due to the nature of module loading and reloading for Blender add-ons,
# several linting errors are temporarily ignored.
# pylint: disable=C0413,E0401,E0601,W0406

# Support reloading of add-on.
if "bpy" in locals():
    import importlib
    if "operators" in locals():
        importlib.reload(operators)
    if "preferences" in locals():
        importlib.reload(preferences)
    if "properties" in locals():
        importlib.reload(properties)
    if "ui" in locals():
        importlib.reload(ui)
    if "utils" in locals():
        importlib.reload(utils)
else:
    from . import operators, preferences, properties, ui, utils

import bpy

# pylint: enable=C0413,E0401,E0601,W0406

_addon_keymaps = []


def _register_keymaps() -> None:
    """Registers Autoflow keymaps."""
    key_configs = bpy.context.window_manager.keyconfigs
    keymap = key_configs.addon.keymaps.new(
        "3D View", space_type="VIEW_3D", region_type="WINDOW"
    )
    keymap.keymap_items.new("autoflow.remesh_dialog", "R", "PRESS", ctrl=True)
    _addon_keymaps.append(keymap)


def _unregister_keymaps() -> None:
    """Unregisters Autoflow keymaps."""
    key_configs = bpy.context.window_manager.keyconfigs
    for keymap in _addon_keymaps:
        for keymap_item in keymap.keymap_items:
            keymap.keymap_items.remove(keymap_item)
        key_configs.addon.keymaps.remove(keymap)
    _addon_keymaps.clear()


def register() -> None:
    """Registers Autoflow and its keymaps when enabling the add-on."""
    bpy.utils.register_module(__name__)
    _register_keymaps()


def unregister() -> None:
    """Unregisters Autoflow and its keymaps when disabling the add-on."""
    _unregister_keymaps()
    bpy.utils.unregister_module(__name__)
