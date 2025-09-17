"""
Animals Regeneration Script
Destroy and respawn cows based on new density or rotation
"""
import unreal
import json
import random
import math
from datetime import datetime, timedelta

def load_config_v2():
    """Load v2 farm configuration"""
    config_path = unreal.Paths.project_content_dir() + 'Farm/Data/farm_config_v2.json'
    with open(config_path, 'r') as f:
        return json.load(f)

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
    total_area_ha = total_area_m2 / 10000

    # Calculate cow count
    cow_count = int(total_area_ha * stocking_density)
    cow_count = max(min_cows, min(cow_count, max_cows))

    return cow_count

def destroy_all_cows():
    """Remove all existing cow actors"""
    print("Removing existing cows...")

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    cow_actors = [actor for actor in all_actors if 'Cow' in actor.tags]

    for cow in cow_actors:
        unreal.EditorLevelLibrary.destroy_actor(cow)

    print(f"Removed {len(cow_actors)} cows")

def get_paddock_bounds(paddock_index, config):
    """Calculate paddock bounds for given index"""
    paddock_size = config.get('paddock_size_m', [120, 80])

    row = paddock_index // 3
    col = paddock_index % 3

    center_x = 500 * 100 + col * (paddock_size[0] + 20) * 100
    center_y = row * (paddock_size[1] + 20) * 100

    return {
        'center': (center_x, center_y),
        'size': (paddock_size[0] * 100, paddock_size[1] * 100)
    }

def spawn_cows_in_paddock(paddock_index, cow_count, config):
    """Spawn cows in specific paddock"""
    print(f"Spawning {cow_count} cows in paddock {paddock_index}")

    bounds = get_paddock_bounds(paddock_index, config)
    center_x, center_y = bounds['center']
    width, height = bounds['size']

    cylinder_mesh = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cylinder')

    cow_materials = [
        '/Game/Farm/Materials/M_CowBlack',
        '/Game/Farm/Materials/M_CowWhite',
        '/Game/Farm/Materials/M_CowBrown'
    ]

    random.seed(config.get('seed', 42) + paddock_index)

    for i in range(cow_count):
        # Random position within paddock
        margin = 500  # 5m margin
        x = center_x + random.uniform(-width/2 + margin, width/2 - margin)
        y = center_y + random.uniform(-height/2 + margin, height/2 - margin)
        rotation = random.uniform(0, 360)

        # Spawn cow
        cow = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(x, y, 75),
            unreal.Rotator(0, rotation, 0)
        )

        if cow:
            mesh_component = cow.get_component_by_class(unreal.StaticMeshComponent)
            if mesh_component:
                mesh_component.set_static_mesh(cylinder_mesh)
                mesh_component.set_relative_scale3d(unreal.Vector(0.8, 0.8, 1.5))

                # Apply material
                material = unreal.EditorAssetLibrary.load_asset(random.choice(cow_materials))
                if material:
                    mesh_component.set_material(0, material)

            # Add tags
            cow.tags = [
                'Cow',
                f'Paddock_{paddock_index}',
                'WanderRadius:2000',
                'StepSeconds:2.0',
                'MoveSpeed:100'
            ]

            # 10% lying down
            if random.random() < 0.1:
                cow.set_actor_scale3d(unreal.Vector(0.8, 0.8, 0.95))
                cow.tags.append('State:Lying')

def rotate_herd(config):
    """Rotate herd to next paddock"""
    print("Rotating herd to next paddock...")

    # Load current state
    state = load_grazing_state()
    current_paddock = state.get('active_paddock_index', 0)
    last_rotated = datetime.fromisoformat(state['last_rotated_iso'].replace('Z', '+00:00'))

    # Check if rotation is due
    rotation_days = config.get('rotation_days', 2)
    days_since_rotation = (datetime.utcnow() - last_rotated.replace(tzinfo=None)).days

    if days_since_rotation < rotation_days:
        print(f"Rotation not due yet ({days_since_rotation}/{rotation_days} days)")
        return current_paddock

    # Calculate next paddock
    num_paddocks = config.get('paddocks', 6)
    next_paddock = (current_paddock + 1) % num_paddocks

    # Destroy existing cows
    destroy_all_cows()

    # Calculate cow distribution
    total_cows = calculate_cow_count(config)
    active_cows = int(total_cows * 0.95)  # 95% in active paddock
    straggler_cows = total_cows - active_cows  # 5% stragglers

    # Spawn cows in new paddock
    spawn_cows_in_paddock(next_paddock, active_cows, config)

    # Add stragglers in previous paddock
    if straggler_cows > 0:
        spawn_cows_in_paddock(current_paddock, straggler_cows, config)

    # Update state
    new_state = {
        'active_paddock_index': next_paddock,
        'last_rotated_iso': datetime.utcnow().isoformat() + 'Z'
    }
    save_grazing_state(new_state)

    print(f"Herd rotated from paddock {current_paddock} to {next_paddock}")
    return next_paddock

def update_density(new_density):
    """Update stocking density and regenerate animals"""
    print(f"Updating stocking density to {new_density} cows/ha")

    # Load config
    config = load_config_v2()

    # Update density
    config['stocking_density_cows_per_ha'] = new_density

    # Save config
    config_path = unreal.Paths.project_content_dir() + 'Farm/Data/farm_config_v2.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Regenerate animals
    regenerate_animals()

def regenerate_animals():
    """Regenerate all animals based on current config"""
    print("Regenerating animals...")

    # Load config and state
    config = load_config_v2()
    state = load_grazing_state()

    # Destroy existing
    destroy_all_cows()

    # Calculate cow count
    total_cows = calculate_cow_count(config)
    active_paddock = state.get('active_paddock_index', 0)

    # Distribute cows
    active_cows = int(total_cows * 0.95)
    straggler_cows = total_cows - active_cows

    # Spawn in active paddock
    spawn_cows_in_paddock(active_paddock, active_cows, config)

    # Add stragglers
    if active_paddock > 0 and straggler_cows > 0:
        spawn_cows_in_paddock(active_paddock - 1, straggler_cows, config)

    # Save level
    unreal.EditorLevelLibrary.save_current_level()

    print(f"Regenerated {total_cows} cows")

def main():
    """Main entry point for animal regeneration"""
    print("\n=== Animal Regeneration ===\n")

    # Load L2 Animals sublevel
    sublevel = '/Game/Farm/Maps/DairyFarm_L2_Animals'
    if unreal.EditorAssetLibrary.does_asset_exist(sublevel):
        # Focus on animals sublevel
        pass

    # Regenerate based on current config
    regenerate_animals()

    config = load_config_v2()
    total_cows = calculate_cow_count(config)

    print(f"\nTotal cows: {total_cows}")
    print(f"Density: {config.get('stocking_density_cows_per_ha', 2.0)} cows/ha")

if __name__ == '__main__':
    main()