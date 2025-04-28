from pathlib import Path

import cv2
import numpy as np

LOWER_BLUE = np.array([90, 120, 180])
UPPER_BLUE = np.array([130, 255, 255])


def extract_character(path: Path) -> np.ndarray | None:
    image = cv2.imread(path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    blue_box = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(blue_box)

    character_region = image[y:y + h, x:x + w]

    gray = cv2.cvtColor(character_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    char_contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not char_contours:
        return None

    character = max(char_contours, key=cv2.contourArea)
    x2, y2, w2, h2 = cv2.boundingRect(character)

    final_character = character_region[y2:y2 + h2, x2:x2 + w2]

    return final_character[75:-75, 75:-75]


def remove_empty_area(image, lower_blue=np.array([90, 50, 50]), upper_blue=np.array([130, 255, 255]), margin: int = 10):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_non_blue = cv2.bitwise_not(mask_blue)

    kernel = np.ones((15, 15), np.uint8)
    mask_char_dilated = cv2.dilate(mask_non_blue, kernel, iterations=1)

    contours, _ = cv2.findContours(mask_char_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    x = max(0, x - margin)
    y = max(0, y - margin)
    w = min(image.shape[1] - x, w + 2 * margin)
    h = min(image.shape[0] - y, h + 2 * margin)

    return image[y:y + h, x:x + w]
