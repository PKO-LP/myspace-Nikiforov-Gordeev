import math


def step_angle(angle_deg, speed_deg, dt, paused=False):
    if paused:
        return angle_deg % 360
    return (angle_deg + speed_deg * dt) % 360


def orbit_position(radius, angle_deg):
    rad = math.radians(angle_deg)
    return (radius * math.cos(rad), 0.0, radius * math.sin(rad))


def clamp_zoom(zoom, min_zoom=0.6, max_zoom=2.4):
    return max(min_zoom, min(max_zoom, zoom))
