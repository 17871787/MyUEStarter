import unreal

MAP_PATH = '/Game/Farm/Maps/DairyFarm_L1'

print(f"Creating visible map at: {MAP_PATH}")

# Ensure directories exist
if not unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm'):
    unreal.EditorAssetLibrary.make_directory('/Game/Farm')
if not unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm/Maps'):
    unreal.EditorAssetLibrary.make_directory('/Game/Farm/Maps')

# Create (or overwrite) a level at MAP_PATH
lvl = unreal.EditorLevelLibrary.new_level(MAP_PATH)

# Helpers
def spawn(cls, loc, rot=(0,0,0)):
    return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(*rot))

print("Adding lighting...")
# Sun + sky + fog
sun = spawn(unreal.DirectionalLight, (0,0,3000), (-35,45,0))
if sun:
    light_comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if light_comp:
        light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        light_comp.set_intensity(5.0)
    print("  - Sun added")

sky = spawn(unreal.SkyAtmosphere, (0,0,0))
if sky:
    print("  - Sky atmosphere added")

sli = spawn(unreal.SkyLight, (0,0,0))
if sli:
    print("  - Sky light added")

fog = spawn(unreal.ExponentialHeightFog, (0,0,0))
if fog:
    print("  - Fog added")

print("Adding floor...")
# Floor using Engine basic cube
cube = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')
if cube:
    sma = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0,0,0),
        unreal.Rotator(0,0,0)
    )
    if sma:
        mesh_comp = sma.get_component_by_class(unreal.StaticMeshComponent)
        if mesh_comp:
            mesh_comp.set_static_mesh(cube)
        sma.set_actor_scale3d(unreal.Vector(100,100,1))  # 100m x 100m pad
        sma.set_actor_label("Floor")
        print("  - Floor mesh added (100x100m)")

print("Adding spawn points...")
# PlayerStart + Camera so you don't spawn into nothing
ps = spawn(unreal.PlayerStart, (0,-300,120))
if ps:
    print("  - PlayerStart added")

cam = spawn(unreal.CameraActor, (800,-800,300), (-15,45,0))
if cam:
    print("  - Camera added")

# Add a visible colored cube as landmark
landmark = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor,
    unreal.Vector(0,0,200),
    unreal.Rotator(0,45,0)
)
if landmark:
    mesh_comp = landmark.get_component_by_class(unreal.StaticMeshComponent)
    if mesh_comp:
        mesh_comp.set_static_mesh(cube)
    landmark.set_actor_scale3d(unreal.Vector(2,2,4))  # 2x2x4m pillar
    landmark.set_actor_label("Landmark_Pillar")
    print("  - Landmark pillar added (red cube at center)")

# Save map
print(f"Saving level...")
unreal.EditorLevelLibrary.save_current_level()
print(f"SUCCESS: Created and saved: {MAP_PATH}")

# List all actors to confirm
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
print(f"\nLevel now contains {len(all_actors)} actors:")
for actor in all_actors[:10]:  # First 10
    print(f"  - {actor.get_class().get_name()}: {actor.get_actor_label()}")