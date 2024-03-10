"""Preferences for the Autoflow add-on.

This module contains Autoflow preferences that a user can set in
Blender's File > User Preferences > Add-ons > Mesh > Autoflow.  The
value "QuadriFlow Path" must be set to the path of a QuadriFlow
executable.  The value "QuadriFlow Timeout (seconds)" can optionally be
set to a maximum time allowed for remeshing.
"""

# pylint: disable=E0401
from bpy.props import IntProperty, StringProperty
from bpy.types import AddonPreferences, Context

# pylint: enable=E0401


class AutoflowPreferences(AddonPreferences):  # pylint: disable=R0903
    """
    Preferences for the Autoflow add-on.

    These preferences can be set in the add-on's preferences window.

    Attributes:
        bl_* (Any): Standard Blender Operator attributes.
        quadriflow_path (StringProperty): Path to QuadriFlow executable.
        quadriflow_timeout (IntProperty): QuadriFlow timeout (seconds).

    Methods:
        draw(self, context):
            Draws attributes in the add-on's preferences window.
    """
    bl_idname = __package__

    quadriflow_path = StringProperty(
        name="QuadriFlow Path",
        description="The path to the QuadriFlow executable on this computer",
        subtype="FILE_PATH",
    )

    quadriflow_timeout = IntProperty(
        name="QuadriFlow Timeout (seconds)",
        description="Maximum time in seconds that QuadriFlow is allowed to "
        "remesh an object before a TimeoutExpired exception is raised (set "
        "this value to zero to allow unlimited time for remeshing)",
        min=0,
        default=0,
    )

    def draw(self, context: Context) -> None:  # pylint: disable=W0613
        """Draws attributes in the add-on's preferences window."""
        layout = self.layout
        layout.prop(self, "quadriflow_path")
        split = layout.split(percentage=1 / 3)
        split.label(text="QuadriFlow Timeout (seconds):")
        split.prop(self, "quadriflow_timeout", text="")
