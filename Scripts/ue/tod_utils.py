"""
Time of Day Utilities
Sun rotation and skylight recapture helpers
"""
import unreal

def set_time_of_day(hours):
    """Set time of day by rotating sun and updating skylight"""
    print(f"Setting time of day to {hours} hours")

    # Find sun (directional light)
    sun = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.DirectionalLight) and 'Sun' in actor.tags:
            sun = actor
            break

    if not sun:
        print("Warning: Sun not found")
        return

    # Calculate sun rotation
    # 6am = sunrise (0°), 12pm = noon (90°), 6pm = sunset (180°)
    sun_angle = (hours - 6) * 15  # 15 degrees per hour
    pitch = -sun_angle if sun_angle < 180 else -sun_angle + 360

    # Update sun rotation
    sun.set_actor_rotation(unreal.Rotator(pitch, 45, 0), False)

    # Update sun tag
    new_tags = []
    for tag in sun.tags:
        if not tag.startswith('TimeOfDay:'):
            new_tags.append(tag)
    new_tags.append(f'TimeOfDay:{hours}')
    sun.tags = new_tags

    # Recapture skylight
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.SkyLight):
            sky_component = actor.get_component_by_class(unreal.SkyLightComponent)
            if sky_component:
                sky_component.recapture_sky()
                print("Sky light recaptured")
            break

    # Update atmosphere
    update_atmosphere_for_time(hours)

    print(f"Time of day set to {hours} hours")

def toggle_day_night():
    """Toggle between day (13:00) and night (03:00)"""
    print("Toggling day/night...")

    # Find current time
    current_time = 15.5  # Default

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.DirectionalLight) and 'Sun' in actor.tags:
            for tag in actor.tags:
                if tag.startswith('TimeOfDay:'):
                    current_time = float(tag.split(':')[1])
                    break
            break

    # Toggle between day and night
    if current_time < 12:
        new_time = 13.0  # Afternoon
    else:
        new_time = 3.0   # Night

    set_time_of_day(new_time)

def update_atmosphere_for_time(hours):
    """Update fog and atmosphere based on time"""

    # Find exponential height fog
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.ExponentialHeightFog):
            fog_component = actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if fog_component:
                # Adjust fog density based on time
                if 6 <= hours <= 18:  # Daytime
                    fog_component.set_fog_density(0.015)
                    fog_component.set_fog_inscattering_color(
                        unreal.LinearColor(0.8, 0.8, 0.9, 1.0)
                    )
                else:  # Nighttime
                    fog_component.set_fog_density(0.025)
                    fog_component.set_fog_inscattering_color(
                        unreal.LinearColor(0.2, 0.2, 0.3, 1.0)
                    )
            break

def get_current_time():
    """Get current time of day from sun"""
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.DirectionalLight) and 'Sun' in actor.tags:
            for tag in actor.tags:
                if tag.startswith('TimeOfDay:'):
                    return float(tag.split(':')[1])

    return 15.5  # Default

def advance_time(hours_delta):
    """Advance time by specified hours"""
    current = get_current_time()
    new_time = (current + hours_delta) % 24

    set_time_of_day(new_time)

def create_time_lapse(start_hour=6, end_hour=20, steps=15):
    """Create time lapse by stepping through hours"""
    print(f"Creating time lapse from {start_hour} to {end_hour} hours")

    hour_step = (end_hour - start_hour) / steps

    for i in range(steps):
        hour = start_hour + (i * hour_step)
        set_time_of_day(hour)

        # Would trigger screenshot here in actual implementation
        print(f"Time lapse frame {i+1}/{steps}: {hour:.1f} hours")

def main():
    """Test time of day utilities"""
    print("\n=== Time of Day Utilities ===\n")

    # Get current time
    current = get_current_time()
    print(f"Current time: {current} hours")

    # Test toggle
    toggle_day_night()

    # Test specific time
    set_time_of_day(17.5)

    print("\nTime utilities ready")

if __name__ == '__main__':
    main()