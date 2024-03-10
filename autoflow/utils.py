"""Utilities for the Autoflow add-on.

This module contains utility functions used throughout the Autoflow
add-on.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# pylint: disable=E0401
import bmesh
import bpy
from bpy.props import PointerProperty
from bpy.types import Context, Mesh, Object, Scene, UILayout

# pylint: enable=E0401


def all_elements_are_manifold(elements: Any) -> bool:
    """Determines whether all elements are manifold.

    Elements are typically bmesh vertices or edges but may be any
    objects with an attribute named is_manifold.
    """
    return all(element.is_manifold for element in elements)


def autoflow_is_compatible_with_os() -> bool:
    """Determines whether Autoflow can be used on this OS."""
    return os_is_linux() or os_is_windows()


def add_quadriflow_args_to_layout(layout: UILayout, context: Context) -> UILayout:
    """Adds properties from AutoflowSettings onto a layout."""
    af = getattr(context.scene, __package__)

    layout.prop(af, "min_cost_flow")
    layout.prop(af, "sharp_preserving")
    if sat_flag_is_allowed():
        layout.prop(af, "flip_removal")
    layout.prop(af, "require_manifold")
    layout.prop(af, "resolution")

    return layout


def get_addon_preference(
    addon_name: str, preference: str, default: Optional[Any] = None
) -> Any:
    """Returns a preference from the Blender add-on named addon_name.

    Returns a default value if the preference can't be found.
    """
    addon_preferences = get_addon_preferences(addon_name)
    return addon_preferences.get(preference, default)


def get_addon_preferences(addon_name: str) -> Dict[str, Any]:
    """Returns preferences from the Blender add-on named addon_name."""
    enabled_addons = bpy.context.user_preferences.addons
    if addon_name in enabled_addons:
        return enabled_addons[addon_name].preferences
    return {}


def get_objects_in_scene(
    scene: Scene, objects_to_ignore: Iterable[Object] = ()
) -> List[Object]:
    """Returns objects in the scene.

    Does not consider the visibility or layer of the objects.  Objects
    in objects_to_ignore are excluded.
    """
    return [obj for obj in scene.objects if obj not in objects_to_ignore]


def get_quadriflow_output_path(input_path: Path) -> Path:
    """Returns the path a remeshed object will be output to."""
    output_name = "".join((input_path.stem, "_remeshed", input_path.suffix))
    return input_path.parent / output_name


def get_quadriflow_path_from_addon_prefs() -> Path:
    """Returns the path to the Quadriflow executable.

    This path is set by the user in the Autoflow add-on preferences.
    """
    return Path(
        get_addon_preference(__package__, "quadriflow_path", default="")
    )


def get_quadriflow_timeout_from_addon_prefs() -> int:
    """Returns the timeout value for Quadriflow's remeshing process.

    This path is set by the user in the Autoflow add-on preferences.
    """
    timeout = get_addon_preference(__package__, "quadriflow_timeout", default=0)
    return max(timeout, 0)


def get_selected_objects_in_scene(
    scene: Scene, objects_to_ignore: Iterable[Object] = ()
) -> List[Object]:
    """Returns selected objects in the scene.

    Does not consider the visibility or layer of the objects.  Objects
    in objects_to_ignore are excluded.
    """
    objects = get_objects_in_scene(scene, objects_to_ignore)
    return [obj for obj in objects if obj.select]


def mesh_is_manifold(mesh: Mesh) -> bool:
    """Determines whether a mesh is manifold.

    A mesh is considered manifold if all of its edges and vertices are
    manifold.
    """
    bmesh_obj = bmesh.new()
    bmesh_obj.from_mesh(mesh)

    edges_and_verts_are_manifold = (
        all_elements_are_manifold(bmesh_obj.edges)
        and all_elements_are_manifold(bmesh_obj.verts)
    )

    bmesh_obj.free()
    return edges_and_verts_are_manifold


def object_can_be_remeshed(obj: Object) -> bool:
    """Determines if the object can be remeshed with Autoflow."""
    return object_has_properties(obj, mode="OBJECT", type="MESH", select=True)


def object_has_properties(obj: Object, **properties: Any) -> bool:
    """Determines if obj.key == properties[key] for keys in properties."""
    return all(
        hasattr(obj, key) and getattr(obj, key) == value
        for key, value in properties.items()
    )


def os_is_linux() -> bool:
    """Determines whether OS is Linux-based."""
    return sys.platform.lower().startswith("linux")


def os_is_windows() -> bool:
    """Determines whether OS is Windows-based."""
    return sys.platform.lower().startswith("win")


def quadriflow_path_pref_is_set() -> bool:
    """Determines if quadriflow_path variable is set in the add-on."""
    quadriflow_path = get_quadriflow_path_from_addon_prefs()
    return quadriflow_path != Path("")


def remesh_with_quadriflow(
    input_path: str,
    output_path: str,
    autoflow_args: PointerProperty,
    timeout: Optional[int] = None,
) -> None:
    """Remeshes an obj file using Quadriflow and saves a copy.

    A description of the QuadriFlow args is available here:
    https://github.com/hjwdzh/QuadriFlow.
    """
    quadriflow_cmd = [
        str(get_quadriflow_path_from_addon_prefs()),
        "-mcf" * autoflow_args.min_cost_flow,
        "-sharp" * autoflow_args.sharp_preserving,
        "-sat" * sat_flag_is_allowed() * autoflow_args.flip_removal,
        "-i",
        input_path,
        "-o",
        output_path,
        "-f",
        str(autoflow_args.resolution),
    ]
    subprocess.run(
        quadriflow_cmd,
        check=False,
        timeout=timeout if timeout else None
    )


def sat_flag_is_allowed() -> bool:
    """Determines if the -sat flag can be used with QuadriFlow."""
    return (
        os_is_linux()
        and unix_executable_is_installed("minisat")
        and unix_executable_is_installed("timeout")
    )


def select_only_objects_in_scene(scene: Scene, objects: Iterable[Object]) -> None:
    """Ensures only the specified objects in the scene are selected."""
    for obj in scene.objects:
        obj.select = obj in objects


def unix_executable_is_installed(executable_command: str) -> bool:
    """Determines if an executable is installed on a Unix system."""
    try:
        subprocess.check_output(["which", executable_command])
        return True
    except subprocess.CalledProcessError:
        return False
