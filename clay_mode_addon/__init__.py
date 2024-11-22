bl_info = {
    "name": "Clay Mode",
    "description": "Simplifies enabling/disabling material override in the View Layer.",
    "author": "Tjomma",
    "version": (1, 0),
    "blender": (4, 2, 2),
    "category": "Material"
}

import bpy
from . import addon_updater_ops

class MATERIAL_OT_OverrideToggle(bpy.types.Operator):
    bl_idname = "material.override_toggle"
    bl_label = "Toggle Material Override"
    bl_description = "Enable or disable Material Override in View Layer"

    def execute(self, context):
        view_layer = context.view_layer
        scene = context.scene

        if view_layer.material_override:
            # Store the current material name
            scene['stored_material_override'] = view_layer.material_override.name
            # Disable material override
            view_layer.material_override = None
            self.report({'INFO'}, "Material Override Disabled")
        else:
            # Retrieve the stored material name
            material_name = scene.get('stored_material_override')
            if material_name:
                material = bpy.data.materials.get(material_name)
                if material:
                    view_layer.material_override = material
                    self.report({'INFO'}, f"Material Override Enabled with '{material.name}'")
                else:
                    self.report({'WARNING'}, f"Stored material '{material_name}' not found")
            else:
                self.report({'WARNING'}, "No stored material to enable override")
        return {'FINISHED'}

def draw_material_override_button(self, context):
    layout = self.layout
    view_layer = context.view_layer
    is_enabled = view_layer.material_override is not None

    # Insert the button to the right of the Overlays button
    row = layout.row(align=True)
    row.operator(
        "material.override_toggle",
        text="Override On" if is_enabled else "Override Off",
        icon='MATERIAL' if is_enabled else 'X',
    )

class ClayModeAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        # Add your own preferences UI elements here
        layout.label(text="Clay Mode Addon Preferences")
        
        # Add the Addon Updater settings UI
        addon_updater_ops.update_settings_ui(self, context)

def register():
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(MATERIAL_OT_OverrideToggle)
    bpy.utils.register_class(ClayModeAddonPreferences)
    bpy.types.VIEW3D_HT_header.append(draw_material_override_button)

def unregister():
    addon_updater_ops.unregister()
    bpy.types.VIEW3D_HT_header.remove(draw_material_override_button)
    bpy.utils.unregister_class(MATERIAL_OT_OverrideToggle)
    bpy.utils.unregister_class(ClayModeAddonPreferences)

if __name__ == "__main__":
    register()
