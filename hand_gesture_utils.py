import numpy as np

# ✅ Normalize landmarks relative to wrist (landmark 0)
def normalize_landmarks(landmarks):
    """
    Normalizes landmarks relative to wrist (landmark 0).
    This removes position bias and improves gesture uniqueness.
    """
    if not landmarks or not isinstance(landmarks[0], list) or len(landmarks[0]) != 3:
        return landmarks  # fallback if already flat or malformed

    base_x, base_y, base_z = landmarks[0]
    return [[x - base_x, y - base_y, z - base_z] for x, y, z in landmarks]

# ✅ Flatten + binarize 3D landmarks using dynamic threshold
def flatten_landmarks(landmarks):
    """
    Converts landmark list to flat binary list using mean thresholding.
    """
    # Already binary?
    if all(isinstance(val, int) for val in landmarks):
        return landmarks

    # Normalize for position invariance
    normalized = normalize_landmarks(landmarks)

    # Flatten
    flat = [val for point in normalized for val in point]

    # Dynamic mean threshold
    threshold = np.mean(flat)
    return [1 if val >= threshold else 0 for val in flat]

# ✅ Binary comparison with Hamming distance
def verify_gesture(input_array, stored_array, max_distance=22):
    """
    Compares binary gesture arrays using Hamming distance.
    Returns True if distance ≤ max_distance.
    """
    if not input_array or not stored_array:
        return False

    flat_input = flatten_landmarks(input_array)
    flat_stored = flatten_landmarks(stored_array)

    if len(flat_input) != len(flat_stored):
        print("❌ Gesture array length mismatch")
        return False

    # Hamming distance: count mismatches
    distance = sum(a != b for a, b in zip(flat_input, flat_stored))
    print(f"🖐 Gesture Hamming distance: {distance}")

    return distance <= max_distance
