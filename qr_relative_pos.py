import cv2
import numpy as np
from robomaster import robot, camera
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import time  # Import time module

# --- Your known QR code positions in the world frame ---
# Not used for relative pose calculation, but can be useful for debugging
qr_map = {
    "7": (0, 0, 0),
    "marker_02": (3.5, 1.5, 90),
}

# --- Camera calibration parameters (estimated, replace with actual values if available) ---
camera_matrix = np.array([
    [92.4, 0.0, 160.0],
    [0.0, 90.2, 120.0],
    [0.0, 0.0, 1.0]
], dtype=np.float64)

# Sample distortion coefficients (replace with real values from calibration)
dist_coeffs = np.array([-0.15, 0.12, 0.0, 0.0, -0.01], dtype=np.float64)

# QR code size in meters
qr_size = 0.07  #7 cm

# 3D coordinates of the QR code corners in its local frame (counter-clockwise)
qr_object_points = np.array([
    [0, 0, 0],
    [qr_size, 0, 0],
    [qr_size, qr_size, 0],
    [0, qr_size, 0]
], dtype=np.float32)

def get_qr_corners(decoded_obj):
    points = decoded_obj.polygon
    if len(points) != 4:
        return None
    pts = np.array([(p.x, p.y) for p in points], dtype=np.float32)
    return order_points(pts)

def order_points(pts):
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]      # top-left
    rect[2] = pts[np.argmax(s)]      # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]   # top-right
    rect[3] = pts[np.argmax(diff)]   # bottom-left
    return rect

def pose_from_qr(img_points):
    success, rvec, tvec = cv2.solvePnP(qr_object_points, img_points, camera_matrix, dist_coeffs)
    if not success:
        print("solvePnP failed")
        return None
    # tvec contains the position of the QR code relative to the camera
    return tvec.flatten()

def process_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Manually adjust brightness
    brightness_factor = 1.5  # Increase brightness
    brightened = cv2.convertScaleAbs(gray, alpha=brightness_factor, beta=0)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    denoised = cv2.bilateralFilter(brightened, 9, 75, 75)
    
    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(enhanced, 255, 
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)
    
    return thresh, enhanced, brightened

def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    
    # Adjust camera settings - only use supported methods
    ep_camera.exposure_value = -40
    print(f"Setting exposure value to: {ep_camera.exposure_value}")

    # Add a small delay to let camera settings take effect
    time.sleep(1)

    print("Starting QR relative pose estimation. Press 'q' to exit.")

    while True:
        frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        if frame is None:
            continue
        
        # Process frame with multiple methods
        thresh, enhanced, gray = process_frame(frame)
        
        # Try detection on different image versions
        decoded_objects = []
        for img in [frame, gray, enhanced, thresh]:
            try:
                decoded = pyzbar.decode(img, symbols=[ZBarSymbol.QRCODE])
                if decoded:
                    decoded_objects = decoded
                    break
            except Exception as e:
                continue
                
        # Debug visualization
        debug_frame = np.hstack([gray, enhanced, thresh])
        cv2.imshow("Debug View", debug_frame)
        
        for obj in decoded_objects:
            qr_id = obj.data.decode("utf-8")
            img_points = get_qr_corners(obj)
            if img_points is None:
                continue

            pose = pose_from_qr(img_points)
            if pose is not None:
                x_rel, y_rel, z_rel = pose
                print(f"QR '{qr_id}' relative to robot: x={x_rel:.2f} m, y={y_rel:.2f} m, z={z_rel:.2f} m")

                # Draw QR bounding box and label
                pts = img_points.reshape((-1, 1, 2)).astype(int)
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.putText(frame, f"{qr_id}: ({x_rel:.2f},{y_rel:.2f},{z_rel:.2f})",
                            (pts[0][0][0], pts[0][0][1]-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)
        
        if not decoded_objects:
            print("No QR code detected")
            cv2.putText(frame, "No QR detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # cv2.imshow("QR Relative Pose", frame)
        cv2.imshow("Raw Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
