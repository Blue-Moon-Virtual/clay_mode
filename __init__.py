bl_info = {
    "name": "clay_mode",
    "description": "Simplifies enabling/disabling material override in the View Layer.",
    "author": "Tjomma",
    "version": (1, 4, 0),
    "blender": (4, 2, 2),
    "category": "Material"
}

# Attempt 1

import bpy
from . import addon_updater_ops
import sys
import subprocess
from mathutils import Vector

def ensure_dependencies():
    try:
        import google.generativeai  # Check if library is installed
    except ModuleNotFoundError:
        # Attempt to install the library in Blender's Python environment
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
            import google.generativeai  # Re-import after installation
        except Exception as e:
            print(f"Failed to install google-generativeai: {e}")
            raise ModuleNotFoundError("google-generativeai is not installed and could not be installed.")
        
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


class ClayModeAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Store API key in Blender's persistent preferences
    api_key: bpy.props.StringProperty(
        name="Gemini API Key",
        description="API Key for Gemini generative AI",
        default="",
    )

    prompt_template: bpy.props.StringProperty(
        name="Prompt Template",
        description="Template for the AI-generated summaries. Use {names} to include object names.",
        default="Summarize the following object names into a short descriptive phrase:\n{names}"
    )
    

    # Updater preferences
    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False
    ) 

    updater_interval_months: bpy.props.IntProperty(
        name="Months",
        description="Number of months between checking for updates",
        default=0,
        min=0
    )

    updater_interval_days: bpy.props.IntProperty(
        name="Days",
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
    )

    updater_interval_hours: bpy.props.IntProperty(
        name="Hours",
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )

    updater_interval_minutes: bpy.props.IntProperty(
        name="Minutes",
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout

        # Gemini API Key UI
        layout.label(text="Gemini API Settings")
        layout.prop(self, "api_key")

        layout.label(text="AI Prompt Template")
        layout.prop(self, "prompt_template", text="Prompt")


        # Updater Settings UI
        layout.label(text="Addon Updater Settings")
        addon_updater_ops.update_settings_ui(self, context)



class CLAY_OT_GroupWithSummary(bpy.types.Operator):
    bl_idname = "clay.group_with_summary"
    bl_label = "Group with AI Summary"
    bl_description = "Group selected objects with an AI-generated summarized name"

    def summarize_names(self, names):
        ensure_dependencies()
        import google.generativeai as genai

        prefs = bpy.context.preferences.addons[__name__].preferences
        api_key = prefs.api_key
        prompt_template = prefs.prompt_template

        if not api_key:
            self.report({'ERROR'}, "API Key not set in preferences")
            return "Group"

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Limit to 10 evenly spaced names
            max_names = 10
            if len(names) > max_names:
                step = max(1, len(names) // max_names)
                selected_names = names[::step][:max_names]
            else:
                selected_names = names

            # Generate the prompt using the template
            prompt = prompt_template.format(names=", ".join(selected_names))
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            self.report({'ERROR'}, f"Error summarizing names: {e}")
            return "Group"



    def execute(self, context):
        objs = context.selected_objects
        if not objs:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        names = [obj.name for obj in objs]
        summary = self.summarize_names(names)

        # Get majority collection and bounding box
        col = max(objs[0].users_collection, key=lambda c: sum(o.name in c.objects for o in objs))
        inf, ninf = float('inf'), float('-inf')
        bounds = [inf, ninf, inf, ninf, inf, ninf]
        for obj in objs:
            for corner in obj.bound_box:
                wc = obj.matrix_world @ Vector(corner)
                bounds[0], bounds[1] = min(bounds[0], wc.x), max(bounds[1], wc.x)
                bounds[2], bounds[3] = min(bounds[2], wc.y), max(bounds[3], wc.y)
                bounds[4], bounds[5] = min(bounds[4], wc.z), max(bounds[5], wc.z)
        center = [(bounds[i] + bounds[i+1]) * 0.5 for i in range(0, 6, 2)]
        size = [bounds[i+1] - bounds[i] for i in range(0, 6, 2)]

        # Create Empty
        bpy.ops.object.empty_add(type='CUBE', location=center)
        empty = context.object
        empty.name = summary
        empty.scale = [s * 0.5 for s in size]

        # Link empty to collection
        for c in empty.users_collection:
            c.objects.unlink(empty)
        col.objects.link(empty)

        # Parent with keep transform
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objs:
            obj.select_set(True)
        empty.select_set(True)
        context.view_layer.objects.active = empty
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        self.report({'INFO'}, f"Grouping done with name: {summary}")
        return {'FINISHED'}




class CLAY_PT_GroupPanel(bpy.types.Panel):
    bl_label = "AI Grouping"
    bl_idname = "CLAY_PT_group_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'  # Creates a new "Tool" tab

    def draw(self, context):
        layout = self.layout
        layout.label(text="Group Objects with AI")
        layout.operator("clay.group_with_summary", text="Group with AI Summary")





def register():
    
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(ClayModeAddonPreferences)
    bpy.utils.register_class(MATERIAL_OT_OverrideToggle)
    bpy.utils.register_class(CLAY_OT_GroupWithSummary)
    bpy.types.VIEW3D_HT_header.append(draw_material_override_button)
    bpy.utils.register_class(CLAY_PT_GroupPanel)

def unregister():

    bpy.utils.unregister_class(CLAY_PT_GroupPanel)
    bpy.types.VIEW3D_HT_header.remove(draw_material_override_button)
    bpy.utils.unregister_class(CLAY_OT_GroupWithSummary)
    bpy.utils.unregister_class(MATERIAL_OT_OverrideToggle)
    bpy.utils.unregister_class(ClayModeAddonPreferences)
    addon_updater_ops.unregister()
    
    
    

if __name__ == "__main__":
    register()