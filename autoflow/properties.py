"""Properties used by the Autoflow add-on.

This module contains the AutoflowSettings class that has attributes
used by the add-on's UI and passed to the QuadriFlow remesher.
"""

# pylint: disable=E0401
import bpy
from bpy.props import BoolProperty, IntProperty, PointerProperty
from bpy.types import PropertyGroup

# pylint: enable=E0401


class AutoflowSettings(PropertyGroup):
    """
    Settings used by the Autoflow add-on.

    These settings are used by the add-on's UI and passed to the
    QuadriFlow remesher.

    Attributes:
        flip_removal (BoolProperty): Use SAT solver flag.
        min_cost_flow (BoolProperty): Use min-cost flow flag.
        require_manifold (BoolProperty): Require manifold mesh.
        resolution (IntProperty): Use resolution parameter.
        sharp_preserving (BoolProperty): Use sharp preserving flag.

    Methods:
        register(cls):
            Registers this class with Blender.
        unregister(cls):
            Unregisters this class from Blender.
    """
    @classmethod
    def register(cls) -> None:
        """Registers this class with Blender."""
        setattr(
            bpy.types.Scene,
            __package__,
            PointerProperty(
                name="Autoflow Settings",
                description="Autoflow settings",
                type=cls,
            )
        )

        cls.flip_removal = BoolProperty(
            name="Flip Removal",
            description="Use SAT solver flag in QuadriFlow command",
            default=False,
        )

        cls.min_cost_flow = BoolProperty(
            name="Min-cost Flow",
            description="Use min-cost flow flag in QuadriFlow command",
            default=False,
        )

        cls.require_manifold = BoolProperty(
            name="Require Manifold Input",
            description="Require an input mesh that is manifold",
            default=False,
        )

        cls.resolution = IntProperty(
            name="Resolution",
            description="Use resolution parameter in QuadriFlow command",
            min=1,
            default=1000,
        )

        cls.sharp_preserving = BoolProperty(
            name="Sharp Preserving",
            description="Use sharp preserving flag in QuadriFlow command",
            default=False,
        )

    @classmethod
    def unregister(cls) -> None:
        """Unregisters this class from Blender."""
        delattr(bpy.types.Scene, __package__)
