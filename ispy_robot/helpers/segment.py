import sys
import time
import math

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

import numpy as np
import cv2

def find_contours(img):
	"""
	Detect reasonably-sized contours on a white background
	"""
	blurred = cv2.blur(img, (15, 15))
	kernel = np.ones((5, 5), np.uint8)

	mask = cv2.inRange(blurred, np.array([0, 0, 80]), np.array([255, 55, 255]))

	mask = cv2.bitwise_not(mask)

	mask = cv2.erode(mask, kernel, iterations=1)
	mask = cv2.dilate(mask, kernel, iterations=1)

	contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	return [x for x in contours if cv2.contourArea(x) > 1800]

class Object:
	"""
	A class to encapsulate size, pictures, and positional data for objects
	"""

	def __init__(self, contour, position, pic, angle):
		self.contour = contour
		self.position = position
		self.pics = [pic]
		self.angles = [angle]

	def update(self, contour, position, pic, angle):
		self.contour = contour
		self.position = position
		self.pics.append(pic)
		self.angles.append(angle)

def record_video(camera, motion):
	"""
	Make the robot stand up and record video while looking around
	Returns an array of tuples containing
	"""

	video_client = camera.subscribeCamera("python_client", 1, 2, 12, 5)
	camera.setParameter(1, 11, 0) # Turn off auto-exposure
	camera.setParameter(1, 17, 400) # Set exposure
	camera.setParameter(1, 6, 32) # Adjust gain

	images = []

	motion.setStiffnesses(["HeadYaw", "HeadPitch"], [1.0, 1.0])
	motion.setAngles(["HeadYaw", "HeadPitch"], [0.8, 0.2], 0.15)
	time.sleep(1.25)
	motion.setAngles(["HeadYaw", "HeadPitch"], [-0.8, 0.2], 0.05)
	stop = time.time() + 6
	while stop - time.time() > 0: # Run for 6 seconds
		nao_image = camera.getImageRemote(video_client)
		images.append((nao_image, motion.getAngles("HeadYaw", True)[0]))
		camera.releaseImage(video_client)
	motion.setAngles(["HeadYaw", "HeadPitch"], [0, 0], 0.25)
	motion.setStiffnesses(["HeadYaw", "HeadPitch"], [0.50, 0.50])

	return images

def find_objects():
	"""
	Process the recorded video and determine object information
	Returns an array of Objects
	"""

	broker = ALBroker("broker", "0.0.0.0", 0, "localhost", 9559)

	motion = ALProxy("ALMotion")
	posture = ALProxy("ALRobotPosture")
	camera = ALProxy("ALVideoDevice", "localhost", 9559)

	posture.goToPosture("Stand", 0.5)

	images = record_video(camera, motion)

	fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
	out_video = cv2.VideoWriter('/home/nao/output.avi', fourcc, 20.0, (640, 480))

	objects = []
	old_objects = []

	for pair in images:
		nao_image = pair[0]
		angle = pair[1]
		# Convert NAO Format to OpenCV format
		frame = np.reshape(np.frombuffer(nao_image[6], dtype='%iuint8' % nao_image[2]), (nao_image[1], nao_image[0], nao_image[2]))

		video_frame = frame.copy()
		cv2.putText(video_frame, str(angle), (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255))
		out_video.write(video_frame)

		old_found = []
		new_contours = []

		contours = find_contours(frame)

		for i in range(len(contours)):
			contour = contours[i]
			x, y, w, h = cv2.boundingRect(contour)
			cx = x + w/2
			cy = y + h/2

			a = camera.getAngularPositionFromImagePosition(1, (float(cx)/640, float(cy)/480))
			a[0] += angle

			best = (None, 99999)
			for j in range(len(old_objects)):
				if j in old_found:
					continue
				u = old_objects[j]
				dist = math.sqrt((cx-u.position[0])**2 + (cy-u.position[1])**2)
				if dist < best[1]:
					best = (u, dist)
			if best[1] < 150:
				old_found.append(best[0])
				best[0].update(contour, (cx, cy), frame[y:(y+h), x:(x+w)], a)
			else:
				print best[1]
				new_contours.append(i)

		new_objects = list(old_found)

		for contour in new_contours:
			contour = contours[contour]
			x, y, w, h = cv2.boundingRect(contour)
			cx = x + w/2
			cy = y + h/2
			a = camera.getAngularPositionFromImagePosition(1, (float(cx)/640, float(cy)/480))
			a[0] += angle
			roi = frame[y:(y+h), x:(x+w)]
			obj = Object(contour, (cx, cy), roi, a)
			objects.append(obj)
			new_objects.append(obj)

		old_objects = new_objects
	out_video.release()
	return objects
