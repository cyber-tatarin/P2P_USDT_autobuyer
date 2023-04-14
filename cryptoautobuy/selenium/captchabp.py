import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import requests
from datetime import datetime


def get_position(full_picture_url, puzzle_piece_url, y_pos):
	
	# getting images from url
	full_picture = Image.open(requests.get(full_picture_url, stream=True).raw)
	puzzle_piece = Image.open(requests.get(puzzle_piece_url, stream=True).raw)
	
	# cutting images to only useful area
	box = (90, y_pos - 177 - 33, 300, y_pos - 177 + 33)
	full_picture = full_picture.crop(box)
	
	box = (10, 10, 70, 70)
	puzzle_piece = puzzle_piece.crop(box)
	
	# converting to grayscale
	full_picture_cv2 = cv2.cvtColor(np.array(full_picture), cv2.COLOR_RGB2BGR)
	puzzle_piece_cv2 = cv2.cvtColor(np.array(puzzle_piece), cv2.COLOR_RGB2BGR)
	
	full_picture_cv2_gray = cv2.cvtColor(full_picture_cv2, cv2.COLOR_BGR2GRAY)
	puzzle_piece_cv2_gray = cv2.cvtColor(puzzle_piece_cv2, cv2.COLOR_BGR2GRAY)
	
	# getting canny edge cv2
	edges1 = cv2.Canny(puzzle_piece_cv2_gray, 100, 200)
	edges2 = cv2.Canny(full_picture_cv2_gray, 100, 200)
	
	contours1, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours2, _ = cv2.findContours(edges2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	# performing template comparing
	result = cv2.matchTemplate(edges2, edges1, cv2.TM_CCORR_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	
	# datetime object containing current date and time
	now = datetime.now()
	# dd/mm/YY H:M:S
	dt_string = now.strftime("%Y%m%d-%H%M%S")
	
	# checking script by drawing rectangle around the most matching area
	(h, w) = edges1.shape[:2]
	cv2.rectangle(edges2, max_loc, (max_loc[0] + w, max_loc[1] + h), (255, 0, 0), 5)
	# cv2.imwrite(f'{dt_string}_full.png', edges2)
	#
	# # print(max_loc[0])
	#
	# cv2.imshow('Result', edges2)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	
	# returning x coordinate of the center of the hole
	return max_loc[0]


# if __name__ == '__main__':
# 	get_position(
# 		'https://static.geetest.com/captcha_v4/d2ce0cc595/slide/ec2217bf4b/2023-01-20T11/bg/5fa6d076ff6c416fb4c80aed2d2eb55c.png',
# 		'https://static.geetest.com/captcha_v4/d2ce0cc595/slide/ec2217bf4b/2023-01-20T11/slice/5fa6d076ff6c416fb4c80aed2d2eb55c.png',
# 		357)
