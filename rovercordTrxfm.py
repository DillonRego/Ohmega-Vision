import numpy as np
def cordanitesToRoverCenter(x, y, z):
    """Transforms the real x, y, and z coordinates relative to the rover's "origin".
    Assuming the camera is located at a position of (2.9cm, 23.54cm, 4.965cm)
    away from the origin and is  angled at -33 degrees relative to the YZ plane.
    In order to transform the coordinates from the camera to the origin,
    we need to apply a combination of translation and rotation.
    A 4x4 matrix allows us to represent both the translation and rotation in a single matrix.
    X is left to right, Y is up and down, Z back and forth relative to the camera/origin"""

    cam_angle = -33  # in degrees
    # Coordinates received from the depth camera
    camera_coords = np.array([x, y, z])

    # Translation matrix to translate from camera position to origin position
    translation_matrix = np.array([[1, 0, 0, -2.9],
                                   [0, 1, 0, 23.54],
                                   [0, 0, 1, 4.965],
                                   [0, 0, 0, 1]])

    # Rotation matrix to account for camera angle
    theta = cam_angle * np.pi / 180  # angle in radians
    # Define the rotation matrix as a 4x4 matrix
    rotation_matrix = np.array([[1, 0, 0, 0],
                                [0, np.cos(theta), -np.sin(theta), 0],
                                [0, np.sin(theta), np.cos(theta), 0],
                                [0, 0, 0, 1]])

    # Transform camera coordinates to origin coordinates
    # Using NumPy's @ operator to perform matrix multiplication.
    origin_coords = translation_matrix @ rotation_matrix @ np.append(camera_coords, 1)

    # Extract X, Y, and Z coordinates from the transformed coordinates
    x_origin, y_origin, z_origin, _ = origin_coords

    return x_origin, y_origin, z_origin


if __name__ == '__main__':
    print(cordanitesToRoverCenter(10,10,10))