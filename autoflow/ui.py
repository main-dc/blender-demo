"""User interface for the Autoflow add-on.

This module contains the AutoflowPanel class used to define the add-on's
tools panel.  The panel contains properties used as arguments for
QuadriFlow and a "Remesh" button used to initiate the remeshing process.
"""

# pylint: disable=E0401
from bpy.types import Context, Panel

from .utils import (add_quadriflow_args_to_layout,
                    autoflow_is_compatible_with_os,
                    get_quadriflow_path_from_addon_prefs,
                    object_can_be_remeshed, quadriflow_path_pref_is_set)

# pylint: enable=E0401


class AUTOFLOW_PT_tools_panel(Panel):  # pylint: disable=C0103,R0903
    """
    The Autoflow tools panel.

    This panel contains properties used as arguments for QuadriFlow and
    a "Remesh" button used to initiate the remeshing process.

    Attributes:
        bl_* (Any): Standard Blender Panel attributes.
        layout (bpy.types.UILayout): The layout of the tools panel.

    Methods:
        draw(self, context):
            Draws the add-on's tools panel.
    """
    bl_category = "Tools"
    bl_label = "Autoflow"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def draw(self, context: Context) -> None:
        """Draws the add-on's tools panel."""
        layout = add_quadriflow_args_to_layout(self.layout, context)

        col = layout.column()
        if not quadriflow_path_pref_is_set():
            col.operator(
                "autoflow.remesh",
                text="Set QuadriFlow path",
                icon="ERROR"
            )
            col.enabled = False
        elif not get_quadriflow_path_from_addon_prefs().exists():
            col.operator(
                "autoflow.remesh",
                text="QuadriFlow path not found",
                icon="ERROR"
            )
            col.enabled = False
        elif not object_can_be_remeshed(context.active_object):
            col.operator(
                "autoflow.remesh",
                text="Select a mesh in object mode",
                icon="ERROR"
            )
            col.enabled = False
        elif not autoflow_is_compatible_with_os():
            col.operator(
                "autoflow.remesh",
                text="Autoflow is for Linux or Windows",
                icon="ERROR"
            )
            col.enabled = False
        else:
            col.operator("autoflow.remesh", icon="FILE_TICK")
