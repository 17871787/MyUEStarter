"""
Dairy Farm Scene Generator
Procedurally generates a complete dairy farm level
"""
import unreal
import json
import math
import random

def load_config():
    """Load farm configuration from JSON"""
    config_path = unreal.Paths.project_content_dir() + 'Farm/Data/farm_config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        print("Warning: Could not load config, using defaults")
        return {
            "seed": 42,
            "paddocks": 4,
            "paddock_size_m": [120, 80],
            "yard_origin": [0, 0, 0],
            "cow_count": 60,
            "lane_points": [[-200, 0, 0], [100, 0, 0], [400, 200, 0]],
            "fence_post_spacing_m": 4.0,
            "hedge_density_per_100m": 6,
            "time_of_day_hours": 15.5
        }

def create_or_get_level(level_name='/Game/Farm/Maps/DairyFarm_L1'):
    """Create or load the farm level"""
    # Create directory if needed
    if not unreal.EditorAssetLibrary.does_directory_exist('/Game/Farm/Maps'):
        unreal.EditorAssetLibrary.make_directory('/Game/Farm/Maps')

    # Create or load level
    if unreal.EditorAssetLibrary.does_asset_exist(level_name):
        print(f"Loading existing level: {level_name}")
        unreal.EditorLevelLibrary.load_level(level_name)
    else:
        print(f"Creating new level: {level_name}")
        unreal.EditorLevelLibrary.new_level(level_name)

    return level_name

def get_or_create_mesh(mesh_type='cube', size=(100, 100, 100)):
    """Get a basic mesh, scaled appropriately"""
    mesh = None

    if mesh_type == 'cube':
        mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')
    elif mesh_type == 'cylinder':
        mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cylinder')
    elif mesh_type == 'sphere':
        mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Sphere')
    elif mesh_type == 'cone':
        mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cone')
    elif mesh_type == 'plane':
        mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane')

    if not mesh:
        # Fallback to cube
        mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')

    return mesh

def spawn_static_mesh(mesh, location, rotation=(0, 0, 0), scale=(1, 1, 1), material_path=None):
    """Spawn a static mesh actor in the level"""
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(location[0], location[1], location[2]),
        unreal.Rotator(rotation[0], rotation[1], rotation[2])
    )

    if actor:
        mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if mesh_component:
            mesh_component.set_static_mesh(mesh)
            mesh_component.set_relative_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))

            # Apply material if specified
            if material_path:
                material = unreal.EditorAssetLibrary.load_asset(material_path)
                if material:
                    mesh_component.set_material(0, material)

    return actor

def create_yard_buildings(config):
    """Create the farm yard buildings"""
    print("Creating yard buildings...")

    yard_buildings = config.get('yard_buildings', {})
    yard_origin = config.get('yard_origin', [0, 0, 0])

    # Dairy shed - large rectangular building
    if 'dairy_shed' in yard_buildings:
        shed = yard_buildings['dairy_shed']
        spawn_static_mesh(
            get_or_create_mesh('cube'),
            [yard_origin[0] + shed['position'][0],
             yard_origin[1] + shed['position'][1],
             shed['size'][2] * 50],  # Height/2 in cm
            scale=[shed['size'][0]/10, shed['size'][1]/10, shed['size'][2]/10],
            material_path='/Game/Farm/Materials/M_Concrete'
        )
        # Add roof
        spawn_static_mesh(
            get_or_create_mesh('cube'),
            [yard_origin[0] + shed['position'][0],
             yard_origin[1] + shed['position'][1],
             shed['size'][2] * 100 + 50],
            scale=[shed['size'][0]/10 + 0.2, shed['size'][1]/10 + 0.2, 0.1],
            material_path='/Game/Farm/Materials/M_Roof'
        )

    # Milking parlour
    if 'milking_parlour' in yard_buildings:
        parlour = yard_buildings['milking_parlour']
        spawn_static_mesh(
            get_or_create_mesh('cube'),
            [yard_origin[0] + parlour['position'][0] * 100,
             yard_origin[1] + parlour['position'][1] * 100,
             parlour['size'][2] * 50],
            scale=[parlour['size'][0]/10, parlour['size'][1]/10, parlour['size'][2]/10],
            material_path='/Game/Farm/Materials/M_Concrete'
        )

    # Slurry tank - cylinder
    if 'slurry_tank' in yard_buildings:
        tank = yard_buildings['slurry_tank']
        spawn_static_mesh(
            get_or_create_mesh('cylinder'),
            [yard_origin[0] + tank['position'][0] * 100,
             yard_origin[1] + tank['position'][1] * 100,
             tank['height'] * 50],
            scale=[tank['radius']/5, tank['radius']/5, tank['height']/10],
            material_path='/Game/Farm/Materials/M_Slurry'
        )

    # Feed bunk
    if 'feed_bunk' in yard_buildings:
        bunk = yard_buildings['feed_bunk']
        spawn_static_mesh(
            get_or_create_mesh('cube'),
            [yard_origin[0] + bunk['position'][0] * 100,
             yard_origin[1] + bunk['position'][1] * 100,
             bunk['size'][2] * 50],
            scale=[bunk['size'][0]/10, bunk['size'][1]/10, bunk['size'][2]/10],
            material_path='/Game/Farm/Materials/M_Wood'
        )

    # Water troughs
    if 'water_trough' in yard_buildings:
        trough = yard_buildings['water_trough']
        for pos in trough['positions']:
            spawn_static_mesh(
                get_or_create_mesh('cube'),
                [yard_origin[0] + pos[0] * 100,
                 yard_origin[1] + pos[1] * 100,
                 trough['size'][2] * 50],
                scale=[trough['size'][0]/10, trough['size'][1]/10, trough['size'][2]/10],
                material_path='/Game/Farm/Materials/M_MetalTrough'
            )

def create_paddocks_with_fences(config):
    """Create paddock areas with fence perimeters"""
    print("Creating paddocks with fences...")

    num_paddocks = config.get('paddocks', 4)
    paddock_size = config.get('paddock_size_m', [120, 80])
    fence_spacing = config.get('fence_post_spacing_m', 4.0)

    # Layout paddocks in a grid
    paddock_actors = []

    for i in range(num_paddocks):
        row = i // 2
        col = i % 2

        # Calculate paddock center
        x = 500 * 100 + col * (paddock_size[0] + 20) * 100  # Convert to cm
        y = row * (paddock_size[1] + 20) * 100

        # Create ground plane for paddock
        ground = spawn_static_mesh(
            get_or_create_mesh('plane'),
            [x, y, 0],
            scale=[paddock_size[0]/10, paddock_size[1]/10, 1],
            material_path='/Game/Farm/Materials/M_Grass'
        )

        # Create fence posts around perimeter
        create_fence_perimeter(x, y, paddock_size[0] * 100, paddock_size[1] * 100, fence_spacing * 100)

        # Add some hedges
        create_hedgerow(x, y, paddock_size[0] * 100, paddock_size[1] * 100, config)

        paddock_actors.append((x, y, paddock_size[0] * 100, paddock_size[1] * 100))

    return paddock_actors

def create_fence_perimeter(center_x, center_y, width, height, spacing):
    """Create fence posts and rails around a rectangular area"""
    half_width = width / 2
    half_height = height / 2

    # Calculate positions for posts
    posts = []

    # Top edge
    for x in range(int(-half_width), int(half_width + spacing), int(spacing)):
        posts.append((center_x + x, center_y + half_height, 0))

    # Bottom edge
    for x in range(int(-half_width), int(half_width + spacing), int(spacing)):
        posts.append((center_x + x, center_y - half_height, 0))

    # Left edge
    for y in range(int(-half_height + spacing), int(half_height), int(spacing)):
        posts.append((center_x - half_width, center_y + y, 0))

    # Right edge
    for y in range(int(-half_height + spacing), int(half_height), int(spacing)):
        posts.append((center_x + half_width, center_y + y, 0))

    # Spawn fence posts
    post_mesh = get_or_create_mesh('cube')
    rail_mesh = get_or_create_mesh('cube')

    for i, pos in enumerate(posts):
        # Fence post
        spawn_static_mesh(
            post_mesh,
            [pos[0], pos[1], 100],
            scale=[0.1, 0.1, 2],
            material_path='/Game/Farm/Materials/M_FencePost'
        )

        # Connect rails to next post
        if i < len(posts) - 1:
            next_pos = posts[i + 1]
            mid_x = (pos[0] + next_pos[0]) / 2
            mid_y = (pos[1] + next_pos[1]) / 2

            # Calculate rail length and rotation
            dx = next_pos[0] - pos[0]
            dy = next_pos[1] - pos[1]
            length = math.sqrt(dx*dx + dy*dy) / 100
            angle = math.degrees(math.atan2(dy, dx))

            # Top rail
            spawn_static_mesh(
                rail_mesh,
                [mid_x, mid_y, 150],
                rotation=[0, angle, 0],
                scale=[length, 0.05, 0.1],
                material_path='/Game/Farm/Materials/M_Wood'
            )

            # Bottom rail
            spawn_static_mesh(
                rail_mesh,
                [mid_x, mid_y, 50],
                rotation=[0, angle, 0],
                scale=[length, 0.05, 0.1],
                material_path='/Game/Farm/Materials/M_Wood'
            )

def create_hedgerow(center_x, center_y, width, height, config):
    """Add hedgerow/trees along paddock edges"""
    hedge_density = config.get('hedge_density_per_100m', 6)

    # Simplified hedge placement - corners and some edges
    hedge_positions = [
        (center_x - width/2, center_y - height/2),
        (center_x + width/2, center_y - height/2),
        (center_x - width/2, center_y + height/2),
        (center_x + width/2, center_y + height/2),
    ]

    # Add some along edges
    for i in range(int(hedge_density)):
        t = (i + 1) / (hedge_density + 1)
        hedge_positions.append((center_x - width/2, center_y - height/2 + t * height))
        hedge_positions.append((center_x + width/2, center_y - height/2 + t * height))

    hedge_mesh = get_or_create_mesh('cone')

    for pos in hedge_positions:
        # Spawn tree/hedge
        spawn_static_mesh(
            hedge_mesh,
            [pos[0], pos[1], 250],
            scale=[2, 2, 5],
            material_path='/Game/Farm/Materials/M_Hedge'
        )

def create_farm_lane(config):
    """Create a simple lane using spline points"""
    print("Creating farm lane...")

    lane_points = config.get('lane_points', [])

    if len(lane_points) < 2:
        return

    # Create simple road segments between points
    road_mesh = get_or_create_mesh('cube')

    for i in range(len(lane_points) - 1):
        p1 = lane_points[i]
        p2 = lane_points[i + 1]

        # Calculate segment properties
        mid_x = (p1[0] + p2[0]) / 2 * 100
        mid_y = (p1[1] + p2[1]) / 2 * 100

        dx = (p2[0] - p1[0]) * 100
        dy = (p2[1] - p1[1]) * 100
        length = math.sqrt(dx*dx + dy*dy) / 100
        angle = math.degrees(math.atan2(dy, dx))

        # Spawn road segment
        spawn_static_mesh(
            road_mesh,
            [mid_x, mid_y, 5],
            rotation=[0, angle, 0],
            scale=[length, 4, 0.1],
            material_path='/Game/Farm/Materials/M_DirtRoad'
        )

def place_cows(config, paddock_areas):
    """Place cow placeholders in paddocks"""
    print("Placing cows...")

    cow_count = config.get('cow_count', 60)
    seed = config.get('seed', 42)
    random.seed(seed)

    # Distribute cows across paddocks
    cows_per_paddock = cow_count // len(paddock_areas) if paddock_areas else 0

    cow_mesh = get_or_create_mesh('cylinder')
    cow_materials = [
        '/Game/Farm/Materials/M_CowBlack',
        '/Game/Farm/Materials/M_CowWhite',
        '/Game/Farm/Materials/M_CowBrown'
    ]

    cow_actors = []

    for paddock_idx, (px, py, width, height) in enumerate(paddock_areas):
        for i in range(cows_per_paddock):
            # Random position within paddock (with margin)
            margin = 500  # 5m margin from fence
            x = px + random.uniform(-width/2 + margin, width/2 - margin)
            y = py + random.uniform(-height/2 + margin, height/2 - margin)
            rotation = random.uniform(0, 360)

            # Spawn cow
            cow = spawn_static_mesh(
                cow_mesh,
                [x, y, 75],
                rotation=[0, 0, rotation],
                scale=[0.8, 0.8, 1.5],
                material_path=random.choice(cow_materials)
            )

            if cow:
                # Tag as cow for later simulation
                cow.tags = ['Cow']
                cow_actors.append(cow)

    return cow_actors

def setup_lighting(config):
    """Set up directional light, sky atmosphere, and fog"""
    print("Setting up lighting...")

    time_of_day = config.get('time_of_day_hours', 15.5)

    # Clear existing lights
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, (unreal.DirectionalLight, unreal.SkyLight, unreal.SkyAtmosphere)):
            unreal.EditorLevelLibrary.destroy_actor(actor)

    # Add Directional Light (sun)
    sun_rotation = calculate_sun_rotation(time_of_day)
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0, 0, 1000),
        unreal.Rotator(sun_rotation[0], sun_rotation[1], 0)
    )
    if sun:
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
            fog_component.set_fog_density(0.02)
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

def calculate_sun_rotation(hour):
    """Calculate sun rotation based on time of day (0-24 hours)"""
    # Simple day/night cycle
    # 6am = sunrise (0°), 12pm = noon (90°), 6pm = sunset (180°)
    sun_angle = (hour - 6) * 15  # 15 degrees per hour
    pitch = -sun_angle if sun_angle < 180 else -sun_angle + 360

    return [pitch, 45, 0]  # Pitch, Yaw, Roll

def main():
    """Main generation function"""
    print("\n=== Starting Dairy Farm Generation ===\n")

    # Load configuration
    config = load_config()

    # Create or load level
    level_name = create_or_get_level()

    # Clear existing actors (optional - comment out to preserve existing)
    # unreal.EditorLevelLibrary.clear_actor_selection()

    # Generate farm components
    create_yard_buildings(config)
    paddock_areas = create_paddocks_with_fences(config)
    create_farm_lane(config)
    cow_actors = place_cows(config, paddock_areas)
    setup_lighting(config)

    # Save the level
    unreal.EditorLevelLibrary.save_current_level()

    print(f"\n=== Farm Generation Complete ===")
    print(f"Level: {level_name}")
    print(f"Paddocks: {len(paddock_areas)}")
    print(f"Cows placed: {len(cow_actors)}")
    print(f"Time of day: {config.get('time_of_day_hours', 15.5)} hours")

    return level_name

if __name__ == '__main__':
    main()