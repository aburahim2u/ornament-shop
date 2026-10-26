import base64
import binascii
import logging
import threading
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException


ROOT = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CatalogProduct:
    product_id: int
    category: str
    style: str
    source: Optional[str] = None
    crop_top: float = 0.0


class ProductCatalog:
    def __init__(self):
        self._products = {
            1: CatalogProduct(1, "necklace", "necklace", "solstice.jpg", 0.18),
            2: CatalogProduct(2, "earring", "hoop", "gold_hoop.png"),
            4: CatalogProduct(4, "nose_ring", "hoop", "gold_hoop.png"),
            5: CatalogProduct(5, "necklace", "necklace", "afterglow.jpg"),
            6: CatalogProduct(6, "earring", "stud", "gemstone_stud.png"),
            7: CatalogProduct(7, "bracelet", "bangle"),
            9: CatalogProduct(9, "necklace", "necklace", "daydream.jpg"),
            10: CatalogProduct(10, "nose_ring", "stud", "gemstone_stud.png"),
            11: CatalogProduct(11, "earring", "huggie", "gold_hoop.png"),
            12: CatalogProduct(12, "bracelet", "bangle"),
            13: CatalogProduct(13, "earring", "drop", "carnelian_drop.png"),
            14: CatalogProduct(14, "earring", "hoop", "ribbonlight_hoops.png"),
            15: CatalogProduct(15, "earring", "hoop", "golden_spiral_hoops.png"),
            16: CatalogProduct(16, "earring", "stud", "gemstone_stud.png"),
            17: CatalogProduct(17, "earring", "hoop", "ribbonlight_hoops.png"),
            18: CatalogProduct(18, "bracelet", "bangle"),
            19: CatalogProduct(19, "bracelet", "bangle"),
            20: CatalogProduct(20, "bracelet", "bangle"),
            21: CatalogProduct(21, "bracelet", "bangle"),
        }

    def get(self, product_id):
        return self._products.get(product_id)


class InvalidTryOnRequest(Exception):
    pass


class TryOnRequestValidator:
    MAX_IMAGE_BYTES = 8 * 1024 * 1024
    MAX_PRODUCT_IMAGE_BYTES = 1024 * 1024
    MAX_BANGLES = 6

    def __init__(self, catalog):
        self._catalog = catalog

    def validate(self, payload):
        if not isinstance(payload, dict):
            raise InvalidTryOnRequest("A JSON object is required.")

        image_data = payload.get("image")
        if not isinstance(image_data, str) or "," not in image_data:
            raise InvalidTryOnRequest("A camera frame is required.")

        try:
            encoded = base64.b64decode(image_data.split(",", 1)[1], validate=True)
        except (binascii.Error, ValueError) as error:
            raise InvalidTryOnRequest("The camera frame could not be decoded.") from error

        if not encoded:
            raise InvalidTryOnRequest("The camera frame is empty.")
        if len(encoded) > self.MAX_IMAGE_BYTES:
            raise InvalidTryOnRequest("The camera frame is too large.")

        raw_product_id = payload.get("product_id")
        if isinstance(raw_product_id, bool):
            raise InvalidTryOnRequest("Select a valid catalog product.")
        try:
            product_id = int(raw_product_id)
        except (TypeError, ValueError) as error:
            raise InvalidTryOnRequest("Select a valid catalog product.") from error
        if isinstance(raw_product_id, float) and raw_product_id != product_id:
            raise InvalidTryOnRequest("Select a valid catalog product.")

        product = self._catalog.get(product_id)
        if product is None:
            raise InvalidTryOnRequest("Select a supported necklace, earring, nose ring, or bracelet.")

        bangles = []
        if product.category == "bracelet":
            raw_bangles = payload.get("bangles")
            if raw_bangles is None:
                raw_bangles = [{
                    "product_id": product_id,
                    "product_image": payload.get("product_image"),
                }]
            if not isinstance(raw_bangles, list) or not 1 <= len(raw_bangles) <= self.MAX_BANGLES:
                raise InvalidTryOnRequest("Select between one and six bangles.")

            seen_product_ids = set()
            for raw_bangle in raw_bangles:
                if not isinstance(raw_bangle, dict):
                    raise InvalidTryOnRequest("A selected bangle is invalid.")
                raw_bangle_id = raw_bangle.get("product_id")
                if isinstance(raw_bangle_id, bool):
                    raise InvalidTryOnRequest("Select a valid bangle.")
                try:
                    bangle_id = int(raw_bangle_id)
                except (TypeError, ValueError) as error:
                    raise InvalidTryOnRequest("Select a valid bangle.") from error
                if isinstance(raw_bangle_id, float) and raw_bangle_id != bangle_id:
                    raise InvalidTryOnRequest("Select a valid bangle.")
                bangle_product = self._catalog.get(bangle_id)
                if bangle_product is None or bangle_product.category != "bracelet":
                    raise InvalidTryOnRequest("Select only supported bangles.")
                if bangle_id in seen_product_ids:
                    raise InvalidTryOnRequest("A bangle cannot be selected more than once.")
                seen_product_ids.add(bangle_id)

                raw_product_image = raw_bangle.get("product_image")
                if not isinstance(raw_product_image, str) or not raw_product_image.startswith("data:image/jpeg;base64,"):
                    raise InvalidTryOnRequest("A selected bangle image could not be loaded.")
                try:
                    product_image = base64.b64decode(
                        raw_product_image.split(",", 1)[1], validate=True
                    )
                except (binascii.Error, ValueError) as error:
                    raise InvalidTryOnRequest("A selected bangle image could not be decoded.") from error
                if not product_image:
                    raise InvalidTryOnRequest("A selected bangle image is empty.")
                if len(product_image) > self.MAX_PRODUCT_IMAGE_BYTES:
                    raise InvalidTryOnRequest("A selected bangle image is too large.")
                bangles.append((bangle_product, product_image))

            if bangles[0][0].product_id != product_id:
                raise InvalidTryOnRequest("The first selected bangle must match the requested product.")

        raw_bangle_width = payload.get("bangle_width")
        bangle_width = None
        if raw_bangle_width is not None:
            if isinstance(raw_bangle_width, bool):
                raise InvalidTryOnRequest("The bangle size is invalid.")
            try:
                bangle_width = int(raw_bangle_width)
            except (TypeError, ValueError) as error:
                raise InvalidTryOnRequest("The bangle size is invalid.") from error
            if raw_bangle_width != bangle_width or not 20 <= bangle_width <= 4096:
                raise InvalidTryOnRequest("The bangle size is invalid.")

        return encoded, product, bangles, bangle_width


class FaceLandmarkDetector:
    def __init__(self):
        self._mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )
        self._lock = threading.Lock()

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with self._lock:
            result = self._mesh.process(rgb_frame)
        if not result.multi_face_landmarks:
            return None
        return result.multi_face_landmarks[0].landmark


class HandLandmarkDetector:
    def __init__(self):
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5,
        )
        self._lock = threading.Lock()

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with self._lock:
            result = self._hands.process(rgb_frame)
        if not result.multi_hand_landmarks:
            return None
        return result.multi_hand_landmarks[0].landmark


class JewelryAssetRepository:
    def __init__(self, root):
        self._root = root

    @lru_cache(maxsize=4)
    def load_product(self, filename):
        source_path = self._root / "assets" / "try_on_sources" / filename
        product = cv2.imread(str(source_path), cv2.IMREAD_UNCHANGED)
        if product is None:
            raise FileNotFoundError(f"Try-on product image was not found: {source_path}")
        if product.ndim != 3 or product.shape[2] != 4:
            raise ValueError(f"Try-on product image must have transparency: {source_path}")
        if not np.any(product[:, :, 3]):
            raise ValueError(f"Try-on product image is fully transparent: {source_path}")
        return product

    @lru_cache(maxsize=8)
    def load_bangle(self, encoded_image):
        source = cv2.imdecode(np.frombuffer(encoded_image, dtype=np.uint8), cv2.IMREAD_COLOR)
        if source is None:
            raise ValueError("The selected bracelet image is not a valid PNG.")

        hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        gold = ((hue <= 45) | (hue >= 170)) & (saturation >= 55) & (value >= 35)
        mask = np.where(gold, 255, 0).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        if component_count <= 1:
            raise ValueError("No bracelet could be extracted from the selected image.")

        largest_component = int(stats[1:, cv2.CC_STAT_AREA].max())
        keep_component = stats[:, cv2.CC_STAT_AREA] >= max(4, int(largest_component * 0.001))
        keep_component[0] = False
        bracelet_mask = np.where(keep_component[labels], 255, 0).astype(np.uint8)
        bracelet_mask = cv2.dilate(bracelet_mask, kernel, iterations=1)
        alpha = cv2.GaussianBlur(bracelet_mask, (3, 3), 0.7)
        points = cv2.findNonZero(alpha)
        if points is None:
            raise ValueError("No bracelet could be extracted from the selected image.")

        x, y, width, height = cv2.boundingRect(points)
        bracelet = cv2.cvtColor(source[y:y + height, x:x + width], cv2.COLOR_BGR2BGRA)
        bracelet[:, :, 3] = alpha[y:y + height, x:x + width]
        return bracelet

    @lru_cache(maxsize=3)
    def load_necklace(self, filename, crop_top):
        source_path = self._root / "assets" / "necklace_sources" / filename
        source = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
        if source is None:
            raise FileNotFoundError(f"Necklace source image was not found: {source_path}")

        height, _ = source.shape[:2]
        source = source[int(height * crop_top):]
        hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        gold = ((hue <= 42) | (hue >= 170)) & (saturation >= 45) & (value >= 45)
        bright_jewels = (value >= 100) & (saturation <= 135)
        mask = np.where(gold | bright_jewels, 255, 0).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        if component_count <= 1:
            raise ValueError(f"No jewelry could be extracted from {filename}.")

        minimum_component_area = max(8, int(mask.size * 0.00001))
        keep_component = stats[:, cv2.CC_STAT_AREA] >= minimum_component_area
        keep_component[0] = False
        if not np.any(keep_component):
            raise ValueError(f"No jewelry could be extracted from {filename}.")

        jewelry_mask = np.where(keep_component[labels], 255, 0).astype(np.uint8)
        jewelry_mask = cv2.dilate(jewelry_mask, kernel, iterations=1)
        alpha = cv2.GaussianBlur(jewelry_mask, (3, 3), 0.7)
        points = cv2.findNonZero(alpha)
        if points is None:
            raise ValueError(f"No jewelry could be extracted from {filename}.")

        x, y, width, height = cv2.boundingRect(points)
        jewelry = cv2.cvtColor(source[y:y + height, x:x + width], cv2.COLOR_BGR2BGRA)
        jewelry[:, :, 3] = alpha[y:y + height, x:x + width]
        return jewelry


class JewelryCompositor:
    def __init__(self, asset_repository):
        self._assets = asset_repository

    @staticmethod
    def _point(landmarks, index, width, height):
        point = landmarks[index]
        return np.array([point.x * width, point.y * height], dtype=np.float32)

    def estimate_bangle_width(self, frame, landmarks):
        height, width = frame.shape[:2]
        index_base = self._point(landmarks, 5, width, height)
        little_finger_base = self._point(landmarks, 17, width, height)
        hand_width = np.linalg.norm(little_finger_base - index_base)
        if hand_width < 24:
            return None
        return max(20, int(hand_width * 1.5))

    def composite_bangle(
        self, frame, landmarks, image, bangle_width=None, stack_index=0, stack_count=1
    ):
        height, width = frame.shape[:2]
        wrist = self._point(landmarks, 0, width, height)
        index_base = self._point(landmarks, 5, width, height)
        little_finger_base = self._point(landmarks, 17, width, height)
        across_hand = little_finger_base - index_base
        hand_width = np.linalg.norm(across_hand)
        palm_center = (index_base + little_finger_base) / 2
        toward_fingers = palm_center - wrist
        palm_length = np.linalg.norm(toward_fingers)
        minimum_hand_width = 12 if bangle_width is not None else 24
        if hand_width < minimum_hand_width or palm_length < 20:
            return False

        across_hand /= hand_width
        toward_fingers /= palm_length
        target_width = (
            bangle_width
            if bangle_width is not None
            else self.estimate_bangle_width(frame, landmarks)
        )
        if target_width is None:
            return False
        target_height = max(12, int(target_width * 0.42))
        forearm_direction = -toward_fingers
        edge_distances = [
            (extent - 1 - coordinate) / direction
            if direction > 0
            else (0 - coordinate) / direction
            if direction < 0
            else float("inf")
            for coordinate, direction, extent in zip(
                wrist, forearm_direction, (width, height)
            )
        ]
        max_center_offset = max(0, min(edge_distances) - target_height / 2)
        first_offset = min(target_height * 0.75, max_center_offset)
        remaining_offset = max(0, max_center_offset - first_offset)
        stack_spacing = (
            min(target_height * 0.85, remaining_offset / (stack_count - 1))
            if stack_count > 1
            else 0
        )
        center = wrist + forearm_direction * (
            first_offset + stack_index * stack_spacing
        )
        overlay = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)

        angle = np.arctan2(across_hand[1], across_hand[0])
        vertical_axis = np.array([-across_hand[1], across_hand[0]])
        if np.dot(vertical_axis, toward_fingers) < 0:
            overlay = cv2.flip(overlay, 0)
        overlay = self._rotate_overlay(overlay, -np.degrees(angle))

        palm_outline = np.array(
            [
                self._point(landmarks, 0, width, height),
                self._point(landmarks, 5, width, height),
                self._point(landmarks, 9, width, height),
                self._point(landmarks, 13, width, height),
                self._point(landmarks, 17, width, height),
            ],
            dtype=np.int32,
        )
        hand_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(hand_mask, [palm_outline], 255)
        rear_arc_start = center + toward_fingers * (target_height * 0.08)
        rear_arc_end = center + toward_fingers * (target_height * 0.55)
        rear_arc_half_width = hand_width * 0.55
        rear_arc_occlusion = np.array(
            [
                rear_arc_start - across_hand * rear_arc_half_width,
                rear_arc_start + across_hand * rear_arc_half_width,
                rear_arc_end + across_hand * rear_arc_half_width,
                rear_arc_end - across_hand * rear_arc_half_width,
            ],
            dtype=np.int32,
        )
        cv2.fillPoly(hand_mask, [rear_arc_occlusion], 255)
        kernel_size = max(3, int(hand_width * 0.06) | 1)
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )
        hand_mask = cv2.dilate(hand_mask, kernel, iterations=1)

        left = int(center[0] - overlay.shape[1] / 2)
        top = int(center[1] - overlay.shape[0] / 2)
        crop_left, crop_top = max(0, -left), max(0, -top)
        crop_right = min(overlay.shape[1], width - left)
        crop_bottom = min(overlay.shape[0], height - top)
        if crop_left < crop_right and crop_top < crop_bottom:
            frame_left, frame_top = left + crop_left, top + crop_top
            frame_right, frame_bottom = left + crop_right, top + crop_bottom
            behind_hand = hand_mask[frame_top:frame_bottom, frame_left:frame_right] > 0
            overlay_alpha = overlay[crop_top:crop_bottom, crop_left:crop_right, 3]
            overlay_alpha[behind_hand] = 0

        self._alpha_composite(
            frame,
            overlay,
            left,
            top,
        )
        return True

    def composite(self, frame, landmarks, product, product_image=None, bangle_width=None):
        height, width = frame.shape[:2]
        if product.category == "bracelet":
            if product_image is None:
                raise ValueError("A selected bracelet image is required for bracelet try-on.")
            image = self._assets.load_bangle(product_image)
            return self.composite_bangle(frame, landmarks, image, bangle_width)
        if product.category == "necklace":
            return self._composite_necklace(frame, landmarks, product, width, height)

        face_width = np.linalg.norm(
            self._point(landmarks, 234, width, height)
            - self._point(landmarks, 454, width, height)
        )
        if face_width < 30:
            return False
        if product.source is None:
            raise ValueError(f"No try-on image is configured for product {product.product_id}.")

        image = self._assets.load_product(product.source)
        if product.category == "nose_ring":
            self._composite_nose_ring(frame, landmarks, image, product.style, face_width, width, height)
            return True

        return self._composite_earrings(frame, landmarks, image, product.style, face_width, width, height)

    def composite_bangles(self, frame, landmarks, bangles, bangle_width):
        placed_count = 0
        for stack_index, (_, encoded_image) in enumerate(bangles):
            image = self._assets.load_bangle(encoded_image)
            if self.composite_bangle(
                frame,
                landmarks,
                image,
                bangle_width,
                stack_index,
                len(bangles),
            ):
                placed_count += 1
        return placed_count

    def _composite_necklace(self, frame, landmarks, product, width, height):
        left_cheek = self._point(landmarks, 234, width, height)
        right_cheek = self._point(landmarks, 454, width, height)
        chin = self._point(landmarks, 152, width, height)
        face_width = np.linalg.norm(right_cheek - left_cheek)
        if face_width < 30:
            return False

        necklace = self._assets.load_necklace(product.source, product.crop_top)
        necklace_height, necklace_width = necklace.shape[:2]
        top_y = int(chin[1] + face_width * 0.10)
        target_width = min(int(face_width * 1.4), int(width * 0.9))
        target_height = int(target_width * necklace_height / necklace_width)
        if target_height > height - top_y:
            target_height = height - top_y
            target_width = int(target_height * necklace_width / necklace_height)
        if target_width < 1 or target_height < 1:
            return False

        resized = cv2.resize(necklace, (target_width, target_height), interpolation=cv2.INTER_AREA)
        left = int((left_cheek[0] + right_cheek[0]) / 2 - target_width / 2)
        self._alpha_composite(frame, resized, left, top_y)
        return True

    def _composite_nose_ring(self, frame, landmarks, image, style, face_width, width, height):
        anchor = self._point(landmarks, 98, width, height)
        target_width = max(8, int(face_width * (0.075 if style == "stud" else 0.12)))
        self._composite_at_landmark(
            frame,
            image,
            target_width,
            int(anchor[0]),
            int(anchor[1] + face_width * 0.012),
        )

    def _composite_earrings(self, frame, landmarks, image, style, face_width, width, height):
        scale = 0.10 if style == "stud" else 0.09 if style == "huggie" else 0.10
        target_width = max(10, int(face_width * scale))
        horizontal = (
            self._point(landmarks, 454, width, height)
            - self._point(landmarks, 234, width, height)
        )
        horizontal_length = np.linalg.norm(horizontal)
        if horizontal_length < 1:
            return False
        horizontal /= horizontal_length
        roll_angle = np.degrees(np.arctan2(horizontal[1], horizontal[0]))

        down = self._point(landmarks, 152, width, height) - self._point(landmarks, 10, width, height)
        down -= horizontal * np.dot(down, horizontal)
        down_length = np.linalg.norm(down)
        if down_length < 1:
            return False
        down /= down_length

        left_depth = landmarks[234].z
        right_depth = landmarks[454].z
        visible_sides = ((234, -1), (454, 1))
        if abs(left_depth - right_depth) * width > face_width * 0.45:
            visible_sides = ((234, -1),) if left_depth < right_depth else ((454, 1),)

        if style not in ("stud", "drop"):
            midpoint = image.shape[1] // 2
            earring_images = {
                234: self._crop_to_alpha(image[:, :midpoint]),
                454: self._crop_to_alpha(image[:, midpoint:]),
            }
        else:
            earring = self._crop_to_alpha(image)
            earring_images = {234: earring, 454: earring}

        placed = False
        for landmark_index, direction in visible_sides:
            lobe = self._point(landmarks, landmark_index, width, height)
            lobe += horizontal * direction * face_width * 0.05
            lobe += down * face_width * 0.12
            if not (0 <= lobe[0] < width and 0 <= lobe[1] < height):
                continue

            earring = earring_images[landmark_index]
            if style == "stud":
                self._composite_at_landmark(
                    frame,
                    earring,
                    target_width,
                    int(lobe[0]),
                    int(lobe[1]),
                    -roll_angle,
                )
            else:
                self._composite_top_at_landmark(
                    frame,
                    earring,
                    target_width,
                    int(lobe[0]),
                    int(lobe[1]),
                    -roll_angle,
                )
            placed = True
        return placed

    @staticmethod
    def _crop_to_alpha(image):
        visible = np.where(image[:, :, 3] > 32, 255, 0).astype(np.uint8)
        points = cv2.findNonZero(visible)
        if points is None:
            return image
        x, y, width, height = cv2.boundingRect(points)
        return image[y:y + height, x:x + width]

    @staticmethod
    def _rotate_overlay(image, angle):
        height, width = image.shape[:2]
        center = (width / 2, height / 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        cosine = abs(matrix[0, 0])
        sine = abs(matrix[0, 1])
        rotated_width = int(height * sine + width * cosine)
        rotated_height = int(height * cosine + width * sine)
        matrix[0, 2] += rotated_width / 2 - center[0]
        matrix[1, 2] += rotated_height / 2 - center[1]
        return cv2.warpAffine(
            image,
            matrix,
            (rotated_width, rotated_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0),
        )

    def _composite_top_at_landmark(
        self, frame, image, target_width, anchor_x, anchor_y, angle=0
    ):
        image_height, image_width = image.shape[:2]
        target_height = max(1, int(target_width * image_height / image_width))
        resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
        resized = self._rotate_overlay(resized, angle)
        opaque = np.where(resized[:, :, 3] > 32)
        if not len(opaque[0]):
            return
        top_row = opaque[0].min()
        top_center_x = int(round(opaque[1][opaque[0] == top_row].mean()))
        self._alpha_composite(
            frame,
            resized,
            anchor_x - top_center_x,
            anchor_y - int(top_row),
        )

    def _composite_at_landmark(
        self, frame, image, target_width, center_x, center_y, angle=0
    ):
        image_height, image_width = image.shape[:2]
        target_height = max(1, int(target_width * image_height / image_width))
        resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
        resized = self._rotate_overlay(resized, angle)
        self._alpha_composite(
            frame,
            resized,
            int(center_x - resized.shape[1] / 2),
            int(center_y - resized.shape[0] / 2),
        )

    @staticmethod
    def _alpha_composite(frame, overlay, left, top):
        height, width = frame.shape[:2]
        overlay_height, overlay_width = overlay.shape[:2]
        right = left + overlay_width
        bottom = top + overlay_height
        frame_left, frame_right = max(0, left), min(width, right)
        frame_top, frame_bottom = max(0, top), min(height, bottom)
        if frame_left >= frame_right or frame_top >= frame_bottom:
            return

        crop = overlay[
            frame_top - top:frame_bottom - top,
            frame_left - left:frame_right - left,
        ]
        alpha = crop[:, :, 3:4].astype(np.float32) / 255
        background = frame[frame_top:frame_bottom, frame_left:frame_right].astype(np.float32)
        foreground = crop[:, :, :3].astype(np.float32)
        frame[frame_top:frame_bottom, frame_left:frame_right] = np.clip(
            foreground * alpha + background * (1 - alpha), 0, 255
        ).astype(np.uint8)


class TryOnService:
    def __init__(self, validator, face_detector, hand_detector, compositor):
        self._validator = validator
        self._face_detector = face_detector
        self._hand_detector = hand_detector
        self._compositor = compositor

    def process(self, payload):
        encoded, product, bangles, bangle_width = self._validator.validate(payload)
        frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            raise InvalidTryOnRequest("The camera frame is not a valid image.")

        detector = self._hand_detector if product.category == "bracelet" else self._face_detector
        landmarks = detector.detect(frame)
        placed = False
        placed_bangles = 0
        if landmarks is not None:
            if product.category == "bracelet":
                if bangle_width is None:
                    bangle_width = self._compositor.estimate_bangle_width(frame, landmarks)
                placed_bangles = self._compositor.composite_bangles(
                    frame, landmarks, bangles, bangle_width
                )
                placed = placed_bangles > 0
            else:
                placed = self._compositor.composite(frame, landmarks, product)

        success, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if not success:
            raise RuntimeError("Could not encode the try-on preview.")
        preview = base64.b64encode(jpeg.tobytes()).decode("ascii")
        response = {
            "found": landmarks is not None,
            "placed": placed,
            "category": product.category,
            "preview": "data:image/jpeg;base64," + preview,
        }
        if product.category == "bracelet":
            response["bangle_width"] = bangle_width
            response["placed_bangles"] = placed_bangles
        return response


def create_app(try_on_service=None):
    application = Flask(__name__, static_folder=str(ROOT), static_url_path="")
    application.config["MAX_CONTENT_LENGTH"] = 22 * 1024 * 1024
    if try_on_service is None:
        catalog = ProductCatalog()
        validator = TryOnRequestValidator(catalog)
        try_on_service = TryOnService(
            validator,
            FaceLandmarkDetector(),
            HandLandmarkDetector(),
            JewelryCompositor(JewelryAssetRepository(ROOT)),
        )

    @application.get("/")
    def home():
        return send_from_directory(ROOT, "index.html")

    @application.post("/api/try-on")
    def try_on():
        payload = request.get_json(silent=True)
        try:
            return jsonify(try_on_service.process(payload))
        except InvalidTryOnRequest as error:
            return jsonify(error=str(error)), 400

    @application.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            if request.path.startswith("/api/"):
                return jsonify(error=error.description), error.code
            return error
        LOGGER.exception("Unexpected application error", exc_info=error)
        if request.path.startswith("/api/"):
            return jsonify(error="Try-on processing failed. Please try again."), 500
        return "An unexpected application error occurred.", 500

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
