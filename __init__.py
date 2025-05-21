bl_info = {
    "name": "ClayMode",
    "description": "Simplifies enabling/disabling material override in the View Layer.",
    "author": "Blue Moon Virtual",
    "version": (1, 5, 0),
    "blender": (4, 2, 2),
    "category": "Material"
}

import bpy
from . import addon_updater_ops
import sys
import subprocess
from mathutils import Vector

def create_clay_material():
    """Create a material for architectural visualization:
    - White Principled BSDF for default objects (Object Index = 0)
    - Glass BSDF for objects with Object Index > 0.5
    """
    mat = bpy.data.materials.new(name="M_ClayMode_Override")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Principled BSDF (Default White Material)
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (1, 1, 1, 1)  # White
    principled.inputs['Roughness'].default_value = 0.8  # Smooth surface

    # Create Glass BSDF (Translucent Material)
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.inputs['Color'].default_value = (1, 1, 1, 1)  # Clear glass
    glass.inputs['Roughness'].default_value = 0.05  # Smooth glass

    # Create Mix Shader to blend Principled and Glass
    mix_shader = nodes.new('ShaderNodeMixShader')

    # Create Object Info Node to get Object Index
    object_info = nodes.new('ShaderNodeObjectInfo')

    # Create Math Node to compare Object Index to 0.5
    math = nodes.new('ShaderNodeMath')
    math.operation = 'GREATER_THAN'
    math.inputs[1].default_value = 0.5  # Threshold for glass

    # Create Output Node
    output = nodes.new('ShaderNodeOutputMaterial')

    # Link Nodes
    links.new(object_info.outputs['Object Index'], math.inputs[0])  # Object Index -> Math
    links.new(math.outputs['Value'], mix_shader.inputs['Fac'])      # Math -> Mix Shader Factor
    links.new(principled.outputs['BSDF'], mix_shader.inputs[1])     # Principled -> Mix Shader
    links.new(glass.outputs['BSDF'], mix_shader.inputs[2])          # Glass -> Mix Shader
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])  # Mix Shader -> Output

    return mat

class MATERIAL_OT_OverrideToggle(bpy.types.Operator):
    bl_idname = "material.override_toggle"
    bl_label = "Toggle Material Override"
    bl_description = "Enable or disable Material Override in View Layer"

    def execute(self, context):
        view_layer = context.view_layer
        scene = context.scene

        if view_layer.material_override:
            # Store current material before disabling
            scene['stored_material_override'] = view_layer.material_override.name
            view_layer.material_override = None
            self.report({'INFO'}, "Material Override Disabled")
        else:
            # Try to retrieve or create material
            material = None
            material_name = scene.get('stored_material_override')
            
            if material_name:
                material = bpy.data.materials.get(material_name)
            
            # Create new material if none exists
            if not material:
                material = create_clay_material()
                scene['stored_material_override'] = material.name
                self.report({'INFO'}, "Created new Clay Override Material")
                
            view_layer.material_override = material
            self.report({'INFO'}, f"Material Override Enabled with '{material.name}'")
            
        return {'FINISHED'}

def draw_material_override_button(self, context):
    layout = self.layout
    view_layer = context.view_layer
    is_enabled = view_layer.material_override is not None

    # Insert the button to the right of the Overlays button
    row = layout.row(align=True)
    row.operator(
        "material.override_toggle",
        text="" if is_enabled else "",
        icon='MATERIAL' if is_enabled else 'META_DATA',
    )

@addon_updater_ops.make_annotations

def register():
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(MATERIAL_OT_OverrideToggle)
    bpy.types.VIEW3D_HT_header.append(draw_material_override_button)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_material_override_button)
    bpy.utils.unregister_class(MATERIAL_OT_OverrideToggle)
    addon_updater_ops.unregister()
    
if __name__ == "__main__":
    register()