import cv2
import math
import numpy as np


def locate_cars(image, car_num, row_num, col_num):
    def locate_colored_items(image, color_lower, color_upper, top_n):
        def calc_center(box):
            return sum(point[0] for point in box) / 4, sum(point[1] for point in box) / 4

        image = cv2.GaussianBlur(image, (5, 5), 0)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        image = cv2.inRange(image, color_lower, color_upper)
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        return [
            calc_center(cv2.boxPoints(cv2.minAreaRect(contour)))
            for contour in sorted(contours, key=cv2.contourArea)[-top_n:]
        ]

    def is_precise(number):
        return abs(number - round(number)) < 0.25

    def is_valid(pos):
        return 0 <= pos[0] < row_num and 0 <= pos[1] < col_num

    mark_points = locate_colored_items(image, np.array([35, 43, 35]), np.array([90, 255, 255]), 2)
    if len(mark_points) < 2:
        raise RuntimeError('Missing mark points')
    bl_point, tr_point = mark_points
    if bl_point[0] > tr_point[0]:
        bl_point, tr_point = tr_point, bl_point
    row_width = (bl_point[1] - tr_point[1]) / (row_num + 1)
    col_width = (tr_point[0] - bl_point[0]) / (col_num + 1)

    car_points = locate_colored_items(image, np.array([0, 60, 60]), np.array([6, 255, 255]), car_num)
    if len(car_points) < car_num:
        raise RuntimeError('Missing car points')
    result = []
    for car_point in car_points:
        row_idx = (bl_point[1] - car_point[1]) / row_width - 1
        col_idx = (car_point[0] - bl_point[0]) / col_width - 1
        if is_precise(row_idx) and is_precise(col_idx):
            row_idx = round(row_idx)
            col_idx = round(col_idx)
            result.append([(row_idx, col_idx)])
        elif is_precise(row_idx):
            row_idx = round(row_idx)
            result.append([(row_idx, math.floor(col_idx)), (row_idx, math.ceil(col_idx))])
        elif is_precise(col_idx):
            col_idx = round(col_idx)
            result.append([(math.floor(row_idx), col_idx), (math.ceil(row_idx), col_idx)])
        else:
            raise RuntimeError('Row index and column index are both imprecise')
        for pos in result[-1]:
            if not is_valid(pos):
                raise RuntimeError('Invalid position')

    return result


if __name__ == '__main__':
    image = cv2.imread('testcases/testcase1.jpg')
    print(locate_cars(image, 2, 2, 2))
    image = cv2.imread('testcases/testcase2.jpg')
    print(locate_cars(image, 2, 3, 3))
