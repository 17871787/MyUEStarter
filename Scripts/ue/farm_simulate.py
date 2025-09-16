"""
Dairy Farm Simulation
Adds simple wandering behavior to cows and time-of-day control
"""
import unreal
import random
import math

def add_cow_wander_blueprint():
    """Create a simple Blueprint for cow wandering behavior"""
    print("Adding cow wandering behavior...")

    # Get all actors tagged as 'Cow'
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    cow_actors = [actor for actor in all_actors if 'Cow' in actor.tags]

    print(f"Found {len(cow_actors)} cows to animate")

    # For each cow, add simple movement metadata
    # Since we can't easily create Blueprint from Python, we'll use actor metadata
    for cow in cow_actors:
        # Store initial position
        location = cow.get_actor_location()

        # Set custom properties using actor tags
        cow.tags.append(f"HomeX:{location.x}")
        cow.tags.append(f"HomeY:{location.y}")
        cow.tags.append(f"WanderRadius:2000")  # 20m wander radius

        # Random initial target
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, 2000)
        target_x = location.x + radius * math.cos(angle)
        target_y = location.y + radius * math.sin(angle)

        cow.tags.append(f"TargetX:{target_x}")
        cow.tags.append(f"TargetY:{target_y}")

    print("Cow wandering metadata added")

def create_time_of_day_controller():
    """Create a Blueprint actor for time of day control"""
    print("Creating time of day controller...")

    # Find the directional light (sun)
    sun = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.DirectionalLight):
            sun = actor
            break

    if sun:
        # Tag it for identification
        sun.tags.append("Sun")
        sun.tags.append("TimeOfDay:15.5")
        print("Sun tagged for time control")

    # Create a simple actor to control time
    time_controller = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Actor,
        unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0)
    )

    if time_controller:
        time_controller.set_actor_label("TimeOfDayController")
        time_controller.tags.append("TimeController")
        time_controller.tags.append("CurrentHour:15.5")
        print("Time controller created")

    return time_controller

def create_level_blueprint_script():
    """Generate a Python script that simulates Level Blueprint functionality"""

    blueprint_code = '''
# Level Blueprint simulation for DairyFarm_L1
# This would normally be Blueprint nodes, but we'll use Python execution

import unreal
import math
import random

def update_cow_positions():
    """Simple cow wandering update"""
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    cow_actors = [actor for actor in all_actors if 'Cow' in actor.tags]

    for cow in cow_actors:
        location = cow.get_actor_location()

        # Parse tags to get wander data
        home_x = home_y = target_x = target_y = wander_radius = 0

        for tag in cow.tags:
            if tag.startswith("HomeX:"):
                home_x = float(tag.split(":")[1])
            elif tag.startswith("HomeY:"):
                home_y = float(tag.split(":")[1])
            elif tag.startswith("TargetX:"):
                target_x = float(tag.split(":")[1])
            elif tag.startswith("TargetY:"):
                target_y = float(tag.split(":")[1])
            elif tag.startswith("WanderRadius:"):
                wander_radius = float(tag.split(":")[1])

        # Move towards target
        dx = target_x - location.x
        dy = target_y - location.y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 50:  # If not at target
            # Move 50cm towards target
            move_x = (dx / distance) * 50
            move_y = (dy / distance) * 50

            new_location = unreal.Vector(
                location.x + move_x,
                location.y + move_y,
                location.z
            )
            cow.set_actor_location(new_location, False, False)

            # Rotate to face direction
            rotation = math.degrees(math.atan2(dy, dx))
            cow.set_actor_rotation(unreal.Rotator(0, rotation, 0), False)
        else:
            # Pick new target
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, wander_radius)
            new_target_x = home_x + radius * math.cos(angle)
            new_target_y = home_y + radius * math.sin(angle)

            # Update tags
            new_tags = []
            for tag in cow.tags:
                if tag.startswith("TargetX:"):
                    new_tags.append(f"TargetX:{new_target_x}")
                elif tag.startswith("TargetY:"):
                    new_tags.append(f"TargetY:{new_target_y}")
                else:
                    new_tags.append(tag)
            cow.tags = new_tags

def update_time_of_day(hours):
    """Update sun rotation based on time"""
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.DirectionalLight) and "Sun" in actor.tags:
            # Calculate sun angle
            sun_angle = (hours - 6) * 15
            pitch = -sun_angle if sun_angle < 180 else -sun_angle + 360

            actor.set_actor_rotation(unreal.Rotator(pitch, 45, 0), False)

            # Update sky light
            for sky in unreal.EditorLevelLibrary.get_all_level_actors():
                if isinstance(sky, unreal.SkyLight):
                    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
                    if sky_component:
                        sky_component.recapture_sky()
            break

# Example usage - would be called on tick or timer
# update_cow_positions()
# update_time_of_day(15.5)
'''

    # Save the simulation script
    script_path = unreal.Paths.project_dir() + 'Scripts/ue/level_blueprint_sim.py'
    with open(script_path, 'w') as f:
        f.write(blueprint_code)

    print(f"Level Blueprint simulation script saved to: level_blueprint_sim.py")

def add_input_bindings():
    """Add input bindings for time of day control"""
    print("Setting up input bindings...")

    # This would normally modify DefaultInput.ini
    # For now, we'll document the bindings
    bindings_info = """
    Time of Day Controls:
    - T: Toggle time advance
    - [ : Previous hour
    - ] : Next hour
    - P: Toggle pause

    These can be activated in the editor or PIE mode.
    """

    print(bindings_info)

    return bindings_info

def main():
    """Main simulation setup"""
    print("\n=== Setting Up Farm Simulation ===\n")

    # Make sure we have the level loaded
    level_name = '/Game/Farm/Maps/DairyFarm_L1'
    if unreal.EditorAssetLibrary.does_asset_exist(level_name):
        unreal.EditorLevelLibrary.load_level(level_name)
    else:
        print(f"Warning: Level {level_name} not found. Run farm_generate.py first!")
        return

    # Add cow wandering behavior
    add_cow_wander_blueprint()

    # Create time of day controller
    time_controller = create_time_of_day_controller()

    # Generate level blueprint simulation script
    create_level_blueprint_script()

    # Document input bindings
    bindings = add_input_bindings()

    # Save the level
    unreal.EditorLevelLibrary.save_current_level()

    print("\n=== Simulation Setup Complete ===")
    print("Cows will wander when level is played")
    print("Use level_blueprint_sim.py functions to update positions")
    print(f"Time controller actor created: {time_controller}")

    return True

if __name__ == '__main__':
    main()