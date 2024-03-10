"""Operators for the Autoflow add-on.

This module contains operators used by the Autoflow add-on to perform
remeshing of objects.  The operators are used in the tools panel and in
a popup dialog.
"""

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Set

# pylint: disable=E0401
import bpy
from bpy.types import Context, Event, Operator

from .utils import (add_quadriflow_args_to_layout,
                    autoflow_is_compatible_with_os, get_objects_in_scene,
                    get_quadriflow_output_path,
                    get_quadriflow_path_from_addon_prefs,
                    get_quadriflow_timeout_from_addon_prefs,
                    get_selected_objects_in_scene, mesh_is_manifold,
                    object_can_be_remeshed, quadriflow_path_pref_is_set,
                    remesh_with_quadriflow, select_only_objects_in_scene)

# pylint: enable=E0401


class AutoflowOperator:
    """
    The Autoflow base operator.

    This operator contains attributes and methods to execute remeshing
    but does not contain UI elements.  Subclasses may add a UI.

    Attributes:
        bl_* (Any): Standard Blender Operator attributes.

    Methods:
        poll(self, context):
            Determines whether this operator can be called.
        execute(self, context):
            Executes this operator, remeshing the active object.
    """
    bl_label = "Autoflow Remesh"
    bl_description = "Remesh the active object with QuadriFlow"
    bl_options = {"INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Determines whether this operator can be called."""
        active_obj = context.active_object
        return active_obj is not None and active_obj.mode == "OBJECT"

    def execute(self, context: Context) -> Set[str]:
        """Executes this operator, remeshing the active object."""
        active_obj = context.active_object
        scene = context.scene
        af = getattr(context.scene, __package__)

        if af.require_manifold and not mesh_is_manifold(active_obj.data):
            self.report(  # pylint: disable=E1101
                {"ERROR"},
                "The 'Require Manifold Input' option is set to "
                "True, but the active object's mesh is not manifold, "
                "so the object will not be remeshed.",
            )
            return {"FINISHED"}

        initial_objects = get_objects_in_scene(scene)
        initial_selected_objects = get_selected_objects_in_scene(scene)
        select_only_objects_in_scene(scene, [active_obj])

        with TemporaryDirectory() as temp_directory:
            obj_path = Path(temp_directory).joinpath(active_obj.name + ".obj")

            print("Autoflow is exporting the active object for remeshing now.")
            bpy.ops.export_scene.obj(
                filepath=str(obj_path), use_selection=True, use_triangles=True
            )

            print(
                "Autoflow is remeshing the active object now.  This may take "
                "a while."
            )
            remeshed_path = get_quadriflow_output_path(obj_path)
            timeout = get_quadriflow_timeout_from_addon_prefs()

            try:
                remesh_with_quadriflow(
                    str(obj_path),
                    str(remeshed_path),
                    autoflow_args=af,
                    timeout=timeout
                )
            except PermissionError as err:
                print(err)
                self.report(  # pylint: disable=E1101
                    {"ERROR"},
                    "There was a permission error during QuadriFlow "
                    "processing.  This may happen if Autoflow's QuadriFlow "
                    "path is incorrect or inaccessible.  See Blender's system "
                    "console for details."
                )
            except subprocess.SubprocessError as err:
                print(err)
                self.report(  # pylint: disable=E1101
                    {"ERROR"},
                    "There was a subprocess error during QuadriFlow "
                    "processing.  See Blender's system console for details.",
                )
            else:
                print("Autoflow is importing the remeshed object now.")
                bpy.ops.import_scene.obj(filepath=str(remeshed_path))
                print("Autoflow finished successfully.")

        new_objects = get_objects_in_scene(
            scene, objects_to_ignore=initial_objects
        )
        if new_objects:
            select_only_objects_in_scene(scene, new_objects)
            scene.objects.active = new_objects[-1]
        else:
            select_only_objects_in_scene(scene, initial_selected_objects)

        return {"FINISHED"}


class AUTOFLOW_OT_remesh(Operator, AutoflowOperator):  # pylint: disable=C0103
    """
    The Autoflow operator used in the tools panel.

    Additional information about the operator is found in the Operator
    and AutoflowOperator base classes.
    """
    bl_idname = "autoflow.remesh"


class AUTOFLOW_OT_remesh_dialog(Operator, AutoflowOperator):  # pylint: disable=C0103
    """
    The Autoflow operator used in a popup dialog.

    The popup dialog appears when Ctrl+R is pressed in object mode.
    Additional information about the operator is found in the Operator
    and AutoflowOperator base classes.

    Methods:
        pre_execution_error_message():
            Returns error messages before execution of the operator.
        draw(self, context):
            Draws the add-on's popup dialog.
        invoke(self, context, event):
            Invokes the add-on's popup dialog.
    """
    bl_idname = "autoflow.remesh_dialog"

    @staticmethod
    def pre_execution_error_message() -> str:
        """Returns error messages before execution of the operator."""
        if not quadriflow_path_pref_is_set():
            return (
                "The QuadriFlow Path must be set in the Autoflow add-on "
                "preferences before Autoflow can be used."
            )
        if not get_quadriflow_path_from_addon_prefs().exists():
            return (
                "The QuadriFlow Path that is set in the Autoflow add-on "
                "preferences cannot be found on this computer.  Please "
                "change the QuadriFlow Path."
            )
        if not object_can_be_remeshed(bpy.context.active_object):
            return "A mesh must be selected in object mode to use Autoflow."
        if not autoflow_is_compatible_with_os():
            return "Autoflow is compatible only with Linux and Windows."
        return ""

    def draw(self, context: Context) -> None:
        """Draws the add-on's popup dialog."""
        add_quadriflow_args_to_layout(self.layout, context)

    def invoke(
        self, context: Context, event: Event  # pylint: disable=W0613
    ) -> Set[str]:
        """Invokes the add-on's popup dialog."""
        error_message = self.pre_execution_error_message()
        if error_message:
            return self.report(("ERROR"), error_message)
        return context.window_manager.invoke_props_dialog(self)
