"""
Dairy Farm L2 Scene Generator
Enhanced version with sublevels, density controls, and landscape
"""
import unreal
import json
import math
import random
from datetime import datetime

def load_config_v2():
    """Load v2 farm configuration"""
    config_path = unreal.Paths.project_content_dir() + 'Farm/Data/farm_config_v2.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        print("Warning: Could not load config v2, using defaults")
        return {
            "seed": 42,
            "time_of_day_hours": 15.5,
            "paddocks": 6,
            "paddock_size_m": [120, 80],
            "stocking_density_cows_per_ha": 2.0,
            "min_cows": 30,
            "max_cows": 150
        }

def load_grazing_state():
    """Load grazing rotation state"""
    state_path = unreal.Paths.project_content_dir() + 'Farm/Data/GrazingState.json'
    try:
        with open(state_path, 'r') as f:
            return json.load(f)
    except:
        return {"active_paddock_index": 0, "last_rotated_iso": datetime.utcnow().isoformat() + "Z"}

def save_grazing_state(state):
    """Save grazing rotation state"""
    state_path = unreal.Paths.project_content_dir() + 'Farm/Data/GrazingState.json'
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

def create_l2_levels():
    """Create persistent level and sublevels for L2"""
    print("Creating L2 level structure...")

    # Ensure directories exist
    if not unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm/Maps'):
        unreal.EditorAssetLibrary.make_directory('/Game/Farm/Maps')

    # Create persistent level
    persistent_level = '/Game/Farm/Maps/DairyFarm_L2'
    if not unreal.EditorAssetLibrary.does_asset_exist(persistent_level):
        unreal.EditorLevelLibrary.new_level(persistent_level)
    else:
        unreal.EditorLevelLibrary.load_level(persistent_level)

    # Create sublevels
    sublevel_names = ['DairyFarm_L2_Paddocks', 'DairyFarm_L2_Yard', 'DairyFarm_L2_Animals']

    for sublevel_name in sublevel_names:
        sublevel_path = f'/Game/Farm/Maps/{sublevel_name}'

        # Create sublevel if it doesn't exist
        if not unreal.EditorAssetLibrary.does_asset_exist(sublevel_path):
            # Save current level first
            unreal.EditorLevelLibrary.save_current_level()
            # Create new level for sublevel
            unreal.EditorLevelLibrary.new_level(sublevel_path)
            unreal.EditorLevelLibrary.save_current_level()
            # Return to persistent level
            unreal.EditorLevelLibrary.load_level(persistent_level)

        # Add sublevel to persistent level
        streaming_level = unreal.EditorLevelUtils.add_level_to_world(
            unreal.EditorLevelLibrary.get_editor_world(),
            sublevel_path,
            unreal.LevelStreamingDynamic
        )

        if streaming_level:
            streaming_level.set_should_be_loaded(True)
            streaming_level.set_should_be_visible(True)
            print(f"Added sublevel: {sublevel_name}")

    return persistent_level

def calculate_cow_count(config):
    """Calculate cow count based on paddock area and stocking density"""
    paddock_size = config.get('paddock_size_m', [120, 80])
    num_paddocks = config.get('paddocks', 6)
    stocking_density = config.get('stocking_density_cows_per_ha', 2.0)
    min_cows = config.get('min_cows', 30)
    max_cows = config.get('max_cows', 150)

    # Calculate total area in hectares
    area_per_paddock_m2 = paddock_size[0] * paddock_size[1]
    total_area_m2 = area_per_paddock_m2 * num_paddocks
    total_area_ha = total_area_m2 / 10000  # Convert to hectares

    # Calculate cow count
    cow_count = int(total_area_ha * stocking_density)
    cow_count = max(min_cows, min(cow_count, max_cows))

    print(f"Calculated cow count: {cow_count} (Area: {total_area_ha:.2f} ha, Density: {stocking_density} cows/ha)")
    return cow_count

def create_landscape(size_x=12800, size_y=12800):
    """Create a simple landscape"""
    print("Creating landscape...")

    # Create landscape actor
    landscape = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Landscape,
        unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0)
    )

    if landscape:
        print("Landscape created (using default flat terrain)")
        # Note: Full landscape creation requires complex heightmap import
        # For now, we'll use a flat landscape as placeholder

    return landscape

def add_navmesh_bounds(config):
    """Add NavMeshBoundsVolume for AI navigation"""
    show_navmesh = config.get('show_navmesh', False)

    print("Adding NavMeshBoundsVolume...")

    # Create NavMeshBoundsVolume
    nav_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.NavMeshBoundsVolume,
        unreal.Vector(600 * 100, 400 * 100, 250),  # Center of paddocks area
        unreal.Rotator(0, 0, 0)
    )

    if nav_volume:
        # Set size to cover all paddocks
        nav_volume.set_actor_scale3d(unreal.Vector(30, 20, 5))

        # Control visibility
        nav_volume.set_actor_hidden_in_game(not show_navmesh)

        print(f"NavMeshBoundsVolume added (visible: {show_navmesh})")

    return nav_volume

def create_paddocks_sublevel(config):
    """Generate paddocks in the Paddocks sublevel"""
    print("Generating paddocks sublevel...")

    # Switch to paddocks sublevel
    sublevel_path = '/Game/Farm/Maps/DairyFarm_L2_Paddocks'

    num_paddocks = config.get('paddocks', 6)
    paddock_size = config.get('paddock_size_m', [120, 80])
    fence_spacing = config.get('fence_post_spacing_m', 4.0)

    paddock_actors = []

    # Create mesh assets
    cube_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')
    plane_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane')

    for i in range(num_paddocks):
        row = i // 3
        col = i % 3

        # Calculate paddock center
        x = 500 * 100 + col * (paddock_size[0] + 20) * 100
        y = row * (paddock_size[1] + 20) * 100

        # Create ground plane
        ground = spawn_static_mesh_actor(
            plane_mesh,
            unreal.Vector(x, y, 0),
            unreal.Rotator(0, 0, 0),
            unreal.Vector(paddock_size[0]/10, paddock_size[1]/10, 1)
        )

        if ground:
            # Apply grass material
            apply_material(ground, '/Game/Farm/Materials/M_Grass')

        # Create fence perimeter
        create_fence_perimeter_l2(x, y, paddock_size[0] * 100, paddock_size[1] * 100, fence_spacing * 100)

        # Add hedgerows
        add_hedgerows_l2(x, y, paddock_size[0] * 100, paddock_size[1] * 100, config)

        paddock_actors.append({
            'index': i,
            'center': (x, y),
            'size': (paddock_size[0] * 100, paddock_size[1] * 100)
        })

    return paddock_actors

def create_yard_sublevel(config):
    """Generate farm yard in the Yard sublevel"""
    print("Generating yard sublevel...")

    yard_buildings = config.get('yard_buildings', {})
    yard_origin = [0, 0, 0]

    cube_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')
    cylinder_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cylinder')

    # Dairy shed
    if 'dairy_shed' in yard_buildings:
        shed = yard_buildings['dairy_shed']
        building = spawn_static_mesh_actor(
            cube_mesh,
            unreal.Vector(shed['position'][0] * 100, shed['position'][1] * 100, shed['size'][2] * 50),
            unreal.Rotator(0, 0, 0),
            unreal.Vector(shed['size'][0]/10, shed['size'][1]/10, shed['size'][2]/10)
        )
        apply_material(building, '/Game/Farm/Materials/M_Concrete')

        # Add roof
        roof = spawn_static_mesh_actor(
            cube_mesh,
            unreal.Vector(shed['position'][0] * 100, shed['position'][1] * 100, shed['size'][2] * 100 + 50),
            unreal.Rotator(0, 0, 0),
            unreal.Vector(shed['size'][0]/10 + 0.2, shed['size'][1]/10 + 0.2, 0.1)
        )
        apply_material(roof, '/Game/Farm/Materials/M_Shed_Roof')

    # Milking parlour
    if 'milking_parlour' in yard_buildings:
        parlour = yard_buildings['milking_parlour']
        building = spawn_static_mesh_actor(
            cube_mesh,
            unreal.Vector(parlour['position'][0] * 100, parlour['position'][1] * 100, parlour['size'][2] * 50),
            unreal.Rotator(0, 0, 0),
            unreal.Vector(parlour['size'][0]/10, parlour['size'][1]/10, parlour['size'][2]/10)
        )
        apply_material(building, '/Game/Farm/Materials/M_Concrete')

    # Slurry tank
    if 'slurry_tank' in yard_buildings:
        tank = yard_buildings['slurry_tank']
        tank_actor = spawn_static_mesh_actor(
            cylinder_mesh,
            unreal.Vector(tank['position'][0] * 100, tank['position'][1] * 100, tank['height'] * 50),
            unreal.Rotator(0, 0, 0),
            unreal.Vector(tank['radius']/5, tank['radius']/5, tank['height']/10)
        )
        apply_material(tank_actor, '/Game/Farm/Materials/M_Slurry')

    # Create lane
    create_farm_lane_l2(config)

def create_animals_sublevel(config, paddock_data):
    """Generate cows in the Animals sublevel"""
    print("Generating animals sublevel...")

    # Calculate cow count
    cow_count = calculate_cow_count(config)

    # Load grazing state
    grazing_state = load_grazing_state()
    active_paddock = grazing_state.get('active_paddock_index', 0)

    # Get rotation settings
    rotation_days = config.get('rotation_days', 2)

    # Place cows in active paddock (with 5% stragglers in previous)
    active_cow_count = int(cow_count * 0.95)
    straggler_count = cow_count - active_cow_count

    # Spawn BP_Cow actors
    create_cow_blueprints(active_paddock, active_cow_count, paddock_data)

    # Add stragglers in previous paddock
    if active_paddock > 0:
        create_cow_blueprints(active_paddock - 1, straggler_count, paddock_data)

    # Spawn BP_HerdManager for each paddock
    for paddock in paddock_data:
        create_herd_manager(paddock)

def spawn_static_mesh_actor(mesh, location, rotation, scale):
    """Helper to spawn static mesh actor"""
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        rotation
    )

    if actor:
        mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if mesh_component:
            mesh_component.set_static_mesh(mesh)
            mesh_component.set_relative_scale3d(scale)

    return actor

def apply_material(actor, material_path):
    """Apply material to actor"""
    if actor:
        mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if mesh_component:
            material = unreal.EditorAssetLibrary.load_asset(material_path)
            if material:
                mesh_component.set_material(0, material)

def create_fence_perimeter_l2(center_x, center_y, width, height, spacing):
    """Enhanced fence creation for L2"""
    half_width = width / 2
    half_height = height / 2

    post_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')
    rail_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')

    # Create fence posts along perimeter
    posts = []

    # Calculate post positions for all edges
    for x in range(int(-half_width), int(half_width + spacing), int(spacing)):
        posts.append((center_x + x, center_y + half_height, 0))
        posts.append((center_x + x, center_y - half_height, 0))

    for y in range(int(-half_height + spacing), int(half_height), int(spacing)):
        posts.append((center_x - half_width, center_y + y, 0))
        posts.append((center_x + half_width, center_y + y, 0))

    # Spawn posts and rails
    for i, pos in enumerate(posts):
        # Fence post
        post = spawn_static_mesh_actor(
            post_mesh,
            unreal.Vector(pos[0], pos[1], 100),
            unreal.Rotator(0, 0, 0),
            unreal.Vector(0.1, 0.1, 2)
        )
        apply_material(post, '/Game/Farm/Materials/M_FencePost')

def add_hedgerows_l2(center_x, center_y, width, height, config):
    """Add enhanced hedgerows for L2"""
    hedge_density = config.get('hedge_density_per_100m', 6)
    cone_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cone')

    # Add trees at corners and along edges
    num_trees = int(hedge_density * 2)

    for i in range(num_trees):
        # Random position along edge
        edge = random.choice(['north', 'south', 'east', 'west'])

        if edge == 'north':
            x = center_x + random.uniform(-width/2, width/2)
            y = center_y + height/2
        elif edge == 'south':
            x = center_x + random.uniform(-width/2, width/2)
            y = center_y - height/2
        elif edge == 'east':
            x = center_x + width/2
            y = center_y + random.uniform(-height/2, height/2)
        else:
            x = center_x - width/2
            y = center_y + random.uniform(-height/2, height/2)

        tree = spawn_static_mesh_actor(
            cone_mesh,
            unreal.Vector(x, y, 250),
            unreal.Rotator(0, random.uniform(0, 360), 0),
            unreal.Vector(2, 2, 5)
        )
        apply_material(tree, '/Game/Farm/Materials/M_Hedge')

def create_farm_lane_l2(config):
    """Create enhanced farm lane for L2"""
    lane_points = config.get('lane_points', [])

    if len(lane_points) < 2:
        return

    cube_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')

    for i in range(len(lane_points) - 1):
        p1 = lane_points[i]
        p2 = lane_points[i + 1]

        mid_x = (p1[0] + p2[0]) / 2 * 100
        mid_y = (p1[1] + p2[1]) / 2 * 100

        dx = (p2[0] - p1[0]) * 100
        dy = (p2[1] - p1[1]) * 100
        length = math.sqrt(dx*dx + dy*dy) / 100
        angle = math.degrees(math.atan2(dy, dx))

        road = spawn_static_mesh_actor(
            cube_mesh,
            unreal.Vector(mid_x, mid_y, 5),
            unreal.Rotator(0, angle, 0),
            unreal.Vector(length, 5, 0.1)
        )
        apply_material(road, '/Game/Farm/Materials/M_Gravel_Lane')

def create_cow_blueprints(paddock_index, cow_count, paddock_data):
    """Create BP_Cow actors using Python"""
    print(f"Spawning {cow_count} cows in paddock {paddock_index}")

    if paddock_index >= len(paddock_data):
        return

    paddock = paddock_data[paddock_index]
    center_x, center_y = paddock['center']
    width, height = paddock['size']

    # Use cylinder as cow placeholder
    cylinder_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cylinder')

    cow_materials = [
        '/Game/Farm/Materials/M_CowBlack',
        '/Game/Farm/Materials/M_CowWhite',
        '/Game/Farm/Materials/M_CowBrown'
    ]

    for i in range(cow_count):
        # Random position within paddock
        margin = 500  # 5m margin from fence
        x = center_x + random.uniform(-width/2 + margin, width/2 - margin)
        y = center_y + random.uniform(-height/2 + margin, height/2 - margin)
        rotation = random.uniform(0, 360)

        # Create cow actor
        cow = spawn_static_mesh_actor(
            cylinder_mesh,
            unreal.Vector(x, y, 75),
            unreal.Rotator(0, rotation, 0),
            unreal.Vector(0.8, 0.8, 1.5)
        )

        if cow:
            # Apply random cow material
            apply_material(cow, random.choice(cow_materials))

            # Add cow tags
            cow.tags = ['Cow', f'Paddock_{paddock_index}', 'WanderRadius:2000', 'StepSeconds:2.0', 'MoveSpeed:100']

            # 10% chance of lying down (idle)
            if random.random() < 0.1:
                cow.set_actor_scale3d(unreal.Vector(0.8, 0.8, 0.95))
                cow.tags.append('State:Lying')

def create_herd_manager(paddock):
    """Create BP_HerdManager for paddock"""
    center_x, center_y = paddock['center']

    # Spawn manager actor
    manager = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Actor,
        unreal.Vector(center_x, center_y, 0),
        unreal.Rotator(0, 0, 0)
    )

    if manager:
        manager.set_actor_label(f"HerdManager_Paddock_{paddock['index']}")
        manager.tags = ['HerdManager', f"Paddock_{paddock['index']}", f"Size:{paddock['size']}"]

def setup_lighting_l2(config):
    """Enhanced lighting setup for L2"""
    time_of_day = config.get('time_of_day_hours', 15.5)

    # Clear existing lights
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, (unreal.DirectionalLight, unreal.SkyLight, unreal.SkyAtmosphere)):
            unreal.EditorLevelLibrary.destroy_actor(actor)

    # Add Directional Light (sun)
    sun_angle = (time_of_day - 6) * 15
    pitch = -sun_angle if sun_angle < 180 else -sun_angle + 360

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0, 0, 1000),
        unreal.Rotator(pitch, 45, 0)
    )

    if sun:
        sun.set_actor_label("Sun")
        sun.tags = ['Sun', f'TimeOfDay:{time_of_day}']
        light_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if light_component:
            light_component.set_intensity(5.0)
            light_component.set_light_color(unreal.LinearColor(1.0, 0.95, 0.8))

    # Add Sky Atmosphere
    sky_atmosphere = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyAtmosphere,
        unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0)
    )

    # Add Sky Light
    sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0, 0, 500),
        unreal.Rotator(0, 0, 0)
    )

    if sky_light:
        sky_light_component = sky_light.get_component_by_class(unreal.SkyLightComponent)
        if sky_light_component:
            sky_light_component.set_intensity(1.0)
            sky_light_component.recapture_sky()

    # Add Exponential Height Fog
    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0)
    )

    if fog:
        fog_component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_component:
            fog_component.set_fog_density(0.015)
            fog_component.set_fog_height_falloff(0.2)

    # Add Post Process Volume
    ppv = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PostProcessVolume,
        unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0)
    )

    if ppv:
        ppv.set_actor_scale3d(unreal.Vector(10000, 10000, 10000))
        ppv.unbound = True

def main():
    """Main L2 generation function"""
    print("\n=== Starting Dairy Farm L2 Generation ===\n")

    # Load configurations
    config = load_config_v2()
    grazing_state = load_grazing_state()

    # Set random seed
    random.seed(config.get('seed', 42))

    # Create L2 level structure
    persistent_level = create_l2_levels()

    # Create landscape
    create_landscape()

    # Add NavMesh bounds
    add_navmesh_bounds(config)

    # Generate sublevels
    paddock_data = create_paddocks_sublevel(config)
    create_yard_sublevel(config)
    create_animals_sublevel(config, paddock_data)

    # Setup lighting
    setup_lighting_l2(config)

    # Save all levels
    unreal.EditorLevelLibrary.save_current_level()

    # Calculate final cow count
    final_cow_count = calculate_cow_count(config)

    print(f"\n=== L2 Farm Generation Complete ===")
    print(f"Level: {persistent_level}")
    print(f"Paddocks: {config.get('paddocks', 6)}")
    print(f"Total cows: {final_cow_count}")
    print(f"Active paddock: {grazing_state.get('active_paddock_index', 0)}")
    print(f"Time of day: {config.get('time_of_day_hours', 15.5)} hours")

    return persistent_level

if __name__ == '__main__':
    main()