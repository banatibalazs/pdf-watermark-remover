# import cv2
# import numpy as np
# from modules.utils import add_texts_to_image
#
# TEXTS = ["Press 'D' to dilate the mask.",
#         "Press 'E' to erode the mask.",
#         "Press 'R' to reset the mask.",
#         "Press 'C' to hide/show this text.",
#         "Press 'space' to finish."]
#
# TEXT_COLOR = (255, 255, 255)
#
#
# class MaskRefiner:
#     def __init__(self, bgr_images, gray_mask):
#         self.images = bgr_images
#         self.mask = gray_mask
#         self.final_mask = None
#         self.median_image = self.calc_median_image()
#         self.threshold_min = 0
#         self.threshold_max = 195
#         self.thresholded_mask = None
#         self.drawn_mask = None
#         self.texts = TEXTS
#         self.text_color = TEXT_COLOR
#         self.text_pos = (10, 40)
#         self.is_text_shown = True
#         self.cursor_size = 5
#
#     def calc_median_image(self, length=40):
#         length = min(length, len(self.images))
#         stacked_images = np.stack([np.array(image) for image in self.images[:length]], axis=-1)
#         median_image = np.median(stacked_images, axis=-1)
#         median_image = np.uint8(median_image)
#         median_image_gray = cv2.cvtColor(median_image, cv2.COLOR_BGR2GRAY)
#         median_image_gray = cv2.bitwise_and(median_image_gray, self.mask)
#         return median_image_gray
#
#     def threshold_mask(self):
#         cv2.imshow('watermark remover', self.median_image)
#         cv2.createTrackbar('th_min', 'watermark remover', self.threshold_min, 255, self.on_threshold_trackbar_min)
#         cv2.createTrackbar('th_max', 'watermark remover', self.threshold_max, 255, self.on_threshold_trackbar_max)
#         cv2.waitKey(0)
#
#     def on_threshold_trackbar_min(self, pos):
#         self.threshold_min = pos
#         self.update_median()
#
#     def on_threshold_trackbar_max(self, pos):
#         self.threshold_max = pos
#         self.update_median()
#
#     def update_median(self):
#         self.thresholded_mask = cv2.inRange(self.median_image, self.threshold_min, self.threshold_max)
#         self.thresholded_mask = cv2.bitwise_and(self.thresholded_mask, self.mask)
#         cv2.imshow('watermark remover', self.thresholded_mask)
#
#     def draw_on_mask(self):
#         self.drawn_mask = self.thresholded_mask.copy()
#         def draw_circle(event, x, y, flags, param):
#             if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
#                 cv2.circle(self.drawn_mask, (x, y), self.cursor_size, (0), -1)
#             elif event == cv2.EVENT_RBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON):
#                 cv2.circle(self.drawn_mask, (x, y), self.cursor_size, (255), -1)
#             elif event == cv2.EVENT_MOUSEWHEEL:
#                 if flags > 0:
#                     self.cursor_size = min(self.cursor_size + 1, 50)
#                 else:
#                     self.cursor_size = max(self.cursor_size - 1, 1)
#                 print(f"Cursor size: {self.cursor_size}")
#
#             # Draw the cursor perimeter as a white line
#             temp_image = self.drawn_mask.copy()
#             cv2.circle(temp_image, (x, y), self.cursor_size, (255), 1)
#             cv2.imshow('watermark remover', temp_image)
#
#         cv2.namedWindow('watermark remover')
#         cv2.setMouseCallback('watermark remover', draw_circle)
#         cv2.imshow('watermark remover', self.drawn_mask)
#         while True:
#             key = cv2.waitKey(1) & 0xFF
#             if key == 32:
#                 break
#             elif key == ord('r'):
#                 self.drawn_mask = self.thresholded_mask.copy()
#                 cv2.imshow('watermark remover', self.drawn_mask)
#
#         cv2.destroyAllWindows()
#
#     def erode_dilate_mask(self):
#         self.final_mask = self.drawn_mask.copy()
#         kernel = np.ones((3, 3), np.uint8)
#         texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
#         cv2.imshow('watermark remover', texted_mask)
#         while True:
#             key = cv2.waitKey(1) & 0xFF
#             if key == ord('d'):
#                 self.final_mask = cv2.dilate(self.final_mask, kernel, iterations=1)
#             elif key == ord('e'):
#                 self.final_mask = cv2.erode(self.final_mask, kernel, iterations=1)
#             elif key == ord('r'):
#                 self.final_mask = self.drawn_mask.copy()
#             if self.is_text_shown:
#                 texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
#                 cv2.imshow('watermark remover', texted_mask)
#             else:
#                 cv2.imshow('watermark remover', self.final_mask)
#             if key == ord('c'):
#                 self.is_text_shown = not self.is_text_shown
#             if key == 32:
#                 break
#         cv2.destroyAllWindows()
#
#     def on_cursor_size_trackbar(self, pos):
#         self.cursor_size = pos
#
#     def get_bgr_mask(self):
#         return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)