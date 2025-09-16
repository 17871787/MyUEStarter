"""
Materials Builder for Dairy Farm
Creates basic materials for the farm scene
"""
import unreal

def create_material(name, base_color=(0.5, 0.5, 0.5), roughness=0.8, metallic=0.0):
    """Create a basic material with specified parameters"""
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material_factory = unreal.MaterialFactoryNew()

    # Create package path
    package_path = f'/Game/Farm/Materials/{name}'

    # Check if already exists
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        print(f"Material {name} already exists, skipping...")
        return unreal.EditorAssetLibrary.load_asset(package_path)

    # Create the material asset
    material = asset_tools.create_asset(name, '/Game/Farm/Materials', unreal.Material, material_factory)

    if material:
        # Create material expression nodes
        base_color_node = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -300, 0
        )
        base_color_node.constant = unreal.LinearColor(base_color[0], base_color[1], base_color[2])

        roughness_node = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant, -300, 200
        )
        roughness_node.r = roughness

        metallic_node = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant, -300, 300
        )
        metallic_node.r = metallic

        # Connect nodes to material outputs
        unreal.MaterialEditingLibrary.connect_material_property(
            base_color_node, '',
            unreal.MaterialProperty.MP_BASE_COLOR, material
        )
        unreal.MaterialEditingLibrary.connect_material_property(
            roughness_node, '',
            unreal.MaterialProperty.MP_ROUGHNESS, material
        )
        unreal.MaterialEditingLibrary.connect_material_property(
            metallic_node, '',
            unreal.MaterialProperty.MP_METALLIC, material
        )

        # Compile the material
        unreal.MaterialEditingLibrary.recompile_material(material)

        # Save the asset
        unreal.EditorAssetLibrary.save_asset(package_path)

        print(f"Created material: {name}")
        return material

    return None

def main():
    """Create all farm materials"""
    print("=== Building Farm Materials ===")

    # Ensure directory exists
    if not unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm'):
        unreal.EditorAssetLibrary.make_directory('/Game/Farm')
    if not unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm/Materials'):
        unreal.EditorAssetLibrary.make_directory('/Game/Farm/Materials')

    # Define materials
    materials = [
        ('M_Grass', (0.15, 0.35, 0.05), 0.9, 0.0),      # Green grass
        ('M_DirtRoad', (0.4, 0.3, 0.2), 0.95, 0.0),     # Brown dirt
        ('M_MetalTrough', (0.7, 0.7, 0.75), 0.4, 0.8),  # Metallic trough
        ('M_Slurry', (0.2, 0.25, 0.15), 0.85, 0.0),     # Green-brown slurry
        ('M_Roof', (0.5, 0.45, 0.4), 0.8, 0.1),         # Gray roof
        ('M_Concrete', (0.6, 0.6, 0.6), 0.7, 0.0),      # Concrete
        ('M_Wood', (0.35, 0.25, 0.15), 0.85, 0.0),      # Brown wood
        ('M_Hedge', (0.1, 0.25, 0.05), 0.95, 0.0),      # Dark green hedge
        ('M_CowBlack', (0.1, 0.1, 0.1), 0.8, 0.0),      # Black cow
        ('M_CowWhite', (0.9, 0.9, 0.85), 0.8, 0.0),     # White cow
        ('M_CowBrown', (0.4, 0.25, 0.15), 0.8, 0.0),    # Brown cow
        ('M_FencePost', (0.3, 0.25, 0.2), 0.9, 0.0),    # Fence post
        ('M_Water', (0.2, 0.4, 0.6), 0.2, 0.0)          # Water
    ]

    # Create each material
    created_count = 0
    for mat_params in materials:
        if create_material(*mat_params):
            created_count += 1

    print(f"\n=== Material Creation Complete ===")
    print(f"Created {created_count} materials in /Game/Farm/Materials")

    # Save all assets
    unreal.EditorAssetLibrary.save_directory('/Game/Farm/Materials')

if __name__ == '__main__':
    main()