import base64
import binascii
import threading
from functools import lru_cache
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, jsonify, request, send_from_directory


ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
)
pose = mp.solutions.pose.Pose(
    static_image_mode=True,
    model_complexity=0,
    min_detection_confidence=0.5,
)
face_mesh_lock = threading.Lock()
NECKLACE_SOURCES = {
    1: ("solstice.jpg", 0.18),
    5: ("afterglow.jpg", 0.00),
    9: ("daydream.jpg", 0.00),
}


@lru_cache(maxsize=3)
def load_necklace_asset(product_id):
    source_info = NECKLACE_SOURCES.get(product_id)
    if source_info is None:
        return None

    source_path = ROOT / "assets" / "necklace_sources" / source_info[0]
    source = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
    if source is None:
        return None

    height, width = source.shape[:2]
    source = source[int(height * source_info[1]):]
    hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)
    gold = ((hue <= 42) | (hue >= 170)) & (saturation >= 45) & (value >= 45)
    bright_jewels = (value >= 100) & (saturation <= 135)
    mask = np.where(gold | bright_jewels, 255, 0).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if component_count <= 1:
        return None
    minimum_component_area = max(8, int(mask.size * 0.00001))
    keep_component = stats[:, cv2.CC_STAT_AREA] >= minimum_component_area
    keep_component[0] = False
    if not np.any(keep_component):
        return None
    necklace_mask = np.where(keep_component[labels], 255, 0).astype(np.uint8)
    necklace_mask = cv2.dilate(necklace_mask, kernel, iterations=1)
    alpha = cv2.GaussianBlur(necklace_mask, (3, 3), 0.7)
    points = cv2.findNonZero(alpha)
    if points is None:
        return None
    x, y, crop_width, crop_height = cv2.boundingRect(points)
    necklace = cv2.cvtColor(source[y:y + crop_height, x:x + crop_width], cv2.COLOR_BGR2BGRA)
    necklace[:, :, 3] = alpha[y:y + crop_height, x:x + crop_width]
    return necklace


def composite_necklaces(frame, landmarks, product_ids, pose_landmarks=None):
    height, width = frame.shape[:2]

    def landmark(index):
        point = landmarks[index]
        return np.array([point.x * width, point.y * height], dtype=np.float32)

    left_cheek = landmark(234)
    right_cheek = landmark(454)
    chin = landmark(152)
    face_width = np.linalg.norm(right_cheek - left_cheek)
    if face_width < 30:
        return frame

    center_x = (left_cheek[0] + right_cheek[0]) / 2
    top_y = chin[1] + face_width * 0.2
    target_width = min(int(face_width * 1.15), int(width * 0.9))
    max_bottom = height
    if pose_landmarks is not None:
        left_shoulder = pose_landmarks[11]
        right_shoulder = pose_landmarks[12]
        if min(left_shoulder.visibility, right_shoulder.visibility) >= 0.35:
            shoulder_left = np.array(
                [left_shoulder.x * width, left_shoulder.y * height],
                dtype=np.float32,
            )
            shoulder_right = np.array(
                [right_shoulder.x * width, right_shoulder.y * height],
                dtype=np.float32,
            )
            shoulder_width = np.linalg.norm(shoulder_right - shoulder_left)
            shoulder_center = (shoulder_left + shoulder_right) / 2
            shoulder_drop = shoulder_center[1] - chin[1]
            if shoulder_width > face_width * 1.25 and shoulder_drop > face_width * 0.4:
                center_x = center_x * 0.75 + shoulder_center[0] * 0.25
                target_width = min(target_width, int(shoulder_width * 0.46))
                top_y = chin[1] + min(face_width * 0.24, max(face_width * 0.12, shoulder_drop * 0.18))
                max_bottom = min(height, int(shoulder_center[1] - face_width * 0.04))

    base_top_y = int(top_y)
    base_target_width = target_width
    base_center_x = center_x
    for layer_index, product_id in reversed(list(enumerate(product_ids))):
        necklace = load_necklace_asset(product_id)
        if necklace is None:
            continue

        necklace_height, necklace_width = necklace.shape[:2]
        layer_top_y = base_top_y + int(face_width * 0.12 * layer_index)
        layer_width = min(
            int(base_target_width * (1 + 0.10 * layer_index)),
            int(width * 0.9),
        )
        layer_height = int(layer_width * necklace_height / necklace_width)
        if layer_height > max_bottom - layer_top_y:
            layer_height = max_bottom - layer_top_y
            layer_width = int(layer_height * necklace_width / necklace_height)
        if layer_width < 1 or layer_height < 1:
            continue

        necklace = cv2.resize(necklace, (layer_width, layer_height), interpolation=cv2.INTER_AREA)
        left = int(base_center_x - layer_width / 2)
        right = left + layer_width
        bottom = layer_top_y + layer_height
        frame_left = max(0, left)
        frame_right = min(width, right)
        frame_top = max(0, layer_top_y)
        frame_bottom = min(height, bottom)
        if frame_left >= frame_right or frame_top >= frame_bottom:
            continue

        necklace_left = frame_left - left
        necklace_top = frame_top - layer_top_y
        crop = necklace[
            necklace_top:necklace_top + frame_bottom - frame_top,
            necklace_left:necklace_left + frame_right - frame_left,
        ]
        alpha = crop[:, :, 3:4].astype(np.float32) / 255
        background = frame[frame_top:frame_bottom, frame_left:frame_right].astype(np.float32)
        foreground = crop[:, :, :3].astype(np.float32)
        frame[frame_top:frame_bottom, frame_left:frame_right] = np.clip(
            foreground * alpha + background * (1 - alpha), 0, 255
        ).astype(np.uint8)
    return frame


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.post("/api/try-on")
def try_on():
    payload = request.get_json(silent=True) or {}
    image_data = payload.get("image", "")
    if not isinstance(image_data, str) or "," not in image_data:
        return jsonify(error="A camera frame is required."), 400

    try:
        encoded = base64.b64decode(image_data.split(",", 1)[1], validate=True)
    except (binascii.Error, ValueError):
        return jsonify(error="The camera frame could not be decoded."), 400

    frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify(error="The camera frame is not a valid image."), 400

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    raw_product_ids = payload.get("product_ids")
    if raw_product_ids is None and "product_id" in payload:
        raw_product_ids = [payload["product_id"]]
    if not isinstance(raw_product_ids, list) or not raw_product_ids:
        return jsonify(error="Select at least one necklace."), 400
    if any(not isinstance(product_id, int) or isinstance(product_id, bool) for product_id in raw_product_ids):
        return jsonify(error="Invalid necklace selection."), 400
    product_ids = raw_product_ids
    if (
        len(product_ids) != len(set(product_ids))
        or any(product_id not in NECKLACE_SOURCES for product_id in product_ids)
    ):
        return jsonify(error="Select a necklace from the catalog."), 400
    with face_mesh_lock:
        result = face_mesh.process(rgb_frame)
        pose_result = pose.process(rgb_frame)

    found_face = bool(result.multi_face_landmarks)
    if found_face:
        pose_landmarks = pose_result.pose_landmarks.landmark if pose_result.pose_landmarks else None
        frame = composite_necklaces(
            frame,
            result.multi_face_landmarks[0].landmark,
            product_ids,
            pose_landmarks,
        )

    success, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
    if not success:
        return jsonify(error="Could not encode the preview."), 500

    preview = base64.b64encode(jpeg.tobytes()).decode("ascii")
    return jsonify(found=found_face, preview="data:image/jpeg;base64," + preview)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)

#Test comment