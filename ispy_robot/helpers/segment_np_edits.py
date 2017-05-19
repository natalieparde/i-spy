import sys
sys.path.insert(0, "../../ispy_core/")  # The path (on your computer) to learn_new_object.py
import learn_new_object

import time
import math

#from naoqi import ALProxy
#from naoqi import ALBroker
#from naoqi import ALModule

import numpy as np
import glob
import cv2
import os
import re

import tensorflow as tf
from six.moves import urllib
from scipy.ndimage import label
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.morphology import watershed
import tarfile

# Modified TensorFlow sample code from classify_image.py
class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = os.path.join(
          "model", 'imagenet_2012_challenge_label_map_proto.pbtxt')
    if not uid_lookup_path:
      uid_lookup_path = os.path.join(
          "model", 'imagenet_synset_to_human_label_map.txt')
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.

    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.

    Returns:
      dict from integer node ID to human-readable string.
    """
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]

# Modified TensorFlow sample code from classify_image.py
def maybe_download_and_extract():
   """Download and extract model tar file."""
   dest_directory = "model"
   DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
   if not os.path.exists(dest_directory):
      os.makedirs(dest_directory)
   filename = DATA_URL.split('/')[-1]
   filepath = os.path.join(dest_directory, filename)
   if not os.path.exists(filepath):
      def _progress(count, block_size, total_size):
         sys.stdout.write('\r>> Downloading %s %.1f%%' % (
            filename, float(count * block_size) / float(total_size) * 100.0))
         sys.stdout.flush()
      filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
      print()
      statinfo = os.stat(filepath)
      print('Succesfully downloaded', filename, statinfo.st_size, 'bytes.')
      tarfile.open(filepath, 'r:gz').extractall(dest_directory)

# Modified TensorFlow sample code from classify_image.py
def create_graph():
   """Creates a graph from saved GraphDef file and returns a saver."""
   # Creates graph from saved graph_def.pb.
   with tf.gfile.FastGFile(os.path.join(
      "model", 'classify_image_graph_def.pb'), 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      _ = tf.import_graph_def(graph_def, name='')

# Modified TensorFlow sample code from classify_image.py
def run_inference_on_image(image):
   """Runs inference on an image.

   Args:
    image: Image file name.

   Returns:
    Tuple containng the human-readable object name, and the prediction score for 
    that object.
   """
   top_prediction = (None, None)
   if not tf.gfile.Exists(image):
      tf.logging.fatal('File does not exist %s', image)
   image_data = tf.gfile.FastGFile(image, 'rb').read()

   with tf.Session() as sess:
    # Some useful tensors:
    # 'softmax:0': A tensor containing the normalized prediction across
    #   1000 labels.
    # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
    #   float description of the image.
    # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
    #   encoding of the image.
    # Runs the softmax tensor by feeding the image_data as input to the graph.
      softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
      predictions = sess.run(softmax_tensor,
                           {'DecodeJpeg/contents:0': image_data})
      predictions = np.squeeze(predictions)

      # Creates node ID --> English string lookup.
      node_lookup = NodeLookup()

      top_k = predictions.argsort()[-1:][::-1]  # [-1:] represents the number of predictions to show; this means I only want one of them (the top one) to be shown.      
      for node_id in top_k:
         human_string = node_lookup.id_to_string(node_id)
         score = predictions[node_id]
         top_prediction = (human_string, score)
   return top_prediction

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

   maybe_download_and_extract()

   # Creates graph from saved GraphDef.
   create_graph()

   img_counter == 0
   for pair in images:
      nao_image = pair[0]
      angle = pair[1]
      # Convert NAO Format to OpenCV format
      frame = np.reshape(np.frombuffer(nao_image[6], dtype='%iuint8' % nao_image[2]), (nao_image[1], nao_image[0], nao_image[2]))

      video_frame = frame.copy()
      cv2.putText(video_frame, str(angle), (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255))
      out_video.write(video_frame)
      frame = cv2.imread(path + image_file)

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

      segment_counter = 1
      for contour in new_contours:
         contour = contours[contour]
         x, y, w, h = cv2.boundingRect(contour)
         cx = x + w/2
         cy = y + h/2
         a = camera.getAngularPositionFromImagePosition(1, (float(cx)/640, float(cy)/480))
         a[0] += angle
         roi = frame[y:(y+h), x:(x+w)]

         # Display the segment.
         print "Displaying segment now...."
         cv2.namedWindow("Segment " + str(segment_counter))
         cv2.imshow("Segment " + str(segment_counter), roi)

         # Write the segment to a file so we can look at it later too.
         segment_file_name = "segments/s" + str(segment_counter) + "_img" + str(img_counter) + ".jpg"
         cv2.imwrite(segment_file_name, roi)

         # Use TensorFlow to classify the segment.
         human_string, score = run_inference_on_image(segment_file_name)
         print('%s (score = %.5f)' % (human_string, score))
         cv2.waitKey(0)  # Wait until the image is manually closed to continue.

         obj = Object(contour, (cx, cy), roi, a)
         objects.append(obj)
         new_objects.append(obj)
         segment_counter += 1

      old_objects = new_objects
      img_counter += 1
   out_video.release()
   return objects

def find_objects_computer():
   """
   Process the images located in the specified folder and determine object information
   Returns an array of Objects
   """

   fourcc = cv2.cv.CV_FOURCC('M','J','P','G')

   objects = []
   old_objects = []
   
   path = "/home/parde/Documents/iSpy_images/GameImages/Game1/"
   game1_image_files = glob.glob(os.path.join(path, "*.jpg"))
   maybe_download_and_extract()

   # Creates graph from saved GraphDef.
   create_graph()

   for image_file in game1_image_files:
      print "Reading image: " + image_file
      frame = cv2.imread(image_file)

      old_found = []
      new_contours = []

      contours = find_contours(frame)

      for i in range(len(contours)):
         print "Checking countour:", i
         contour = contours[i]
         x, y, w, h = cv2.boundingRect(contour)
         cx = x + w/2
         cy = y + h/2

         a = math.atan2(float(cx)/640, float(cy)/480)  # May not be an accurate approximation of its counterpart in the robot code.

         best = (None, 99999)
         for j in range(len(old_objects)):
            if j in old_found:
               continue
            u = old_objects[j]
            dist = math.sqrt((cx-u.position[0])**2 + (cy-u.position[1])**2)
            if dist < best[1]:
               best = (u, dist)

         # Note: The code below differs somewhat from the analogous code in find_objects().  
         # I didn't change it in find_objects() because it's possible that when using the 
         # robot, it's better as-is.  However, when using multiple images stored in a 
         # directory, the original code in find_objects() stopped finding new segments 
         # after the first image.  This version finds (or at least tries to find) 
         # segments in all images.
         if best[0] is not None:
            old_found.append(best[0])
            best[0].update(contour, (cx, cy), frame[y:(y+h), x:(x+w)], a)
         new_contours.append(i)

      new_objects = list(old_found)

      segment_counter = 1
      for contour in new_contours:
         contour = contours[contour]
         x, y, w, h = cv2.boundingRect(contour)
         cx = x + w/2
         cy = y + h/2
         a = math.atan2(float(cx)/640, float(cy)/480)

         roi = frame[y:(y+h), x:(x+w)]

         # Display the segment.
         print "Displaying segment now...."
         cv2.namedWindow("Segment " + str(segment_counter))
         cv2.imshow("Segment " + str(segment_counter), roi)

         # Write the segment to a file so we can look at it later too.
         segment_file_name = "segments/s" + str(segment_counter) + "_" + image_file.replace(path, "").strip("/").strip("\\")
         if not os.path.exists("segments"):  # Create the "segments" directory if it does not exist yet.
            os.makedirs("segments")
         cv2.imwrite(segment_file_name, roi)

         # Use TensorFlow to classify the segment.
         object_name, score = run_inference_on_image(segment_file_name)
         print('%s (score = %.5f)' % (object_name, score))
         cv2.waitKey(0)  # Wait until the image is manually closed to continue.

         obj = Object(contour, (cx, cy), roi, a)
         objects.append(obj)
         new_objects.append(obj)
         segment_counter += 1
      old_objects = new_objects
   return [obj.angles for obj in objects]


# Alternate segmentation method (basically followed a variety of online tutorials
# describing how to implement OpenCV's Watershed algorithm).
def find_objects_alternate_seg():
   """
   Process the images located in the specified folder and determine object information
   Returns an array of Objects
   """

 #  fourcc = cv2.cv.CV_FOURCC('M','J','P','G')  # Comment this if using OpenCV 3+
   fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # Comment this if using OpenCV < 3.0

   objects = []
   old_objects = []
   object_names = []  # A list of the names of objects identified in the gamespace (including new objects).
   retrain_models = False

   path = "/home/parde/Documents/iSpy_images/GameImages/Game1/"
   game1_image_files = glob.glob(os.path.join(path, "*.jpg"))
   maybe_download_and_extract()

   # Creates graph from saved GraphDef.
   create_graph()

   for image_file in game1_image_files:
      print "Reading image: " + image_file
      frame = cv2.imread(image_file)
      frame_copy = frame.copy()
      grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      ret, thresh = cv2.threshold(grayscale,0,255, cv2.THRESH_OTSU)

      dt = ndimage.distance_transform_edt(thresh)
      local_max = peak_local_max(dt, indices=False, min_distance=20, labels=thresh)
      markers = ndimage.label(local_max, structure=np.ones((3, 3)))[0]

      labels = watershed(-dt, markers, mask=thresh)

      # Then loop through the segments.
      segment_counter = 0
      for seg in np.unique(labels):
         if seg != 0:  # 0 seems to be the good segments.
            continue

         # Allocate memory for the label region and draw it on the mask.
         mask = np.zeros(grayscale.shape, dtype="uint8")
         mask[labels == seg] = 255

         # Detect contours and get the largest contour.
         contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
         for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            if h < 20 or w < 20:  # Too small of a segment.
               continue
            elif h > 200 or w > 200:  # Too big of a segment.
               continue

            # Draw the minimum rectangle onto the original image.
            min_rectangle = cv2.minAreaRect(contour)
            box = cv2.boxPoints(min_rectangle)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)

            # Display segment.
            roi = frame_copy[y:(y+h), x:(x+w)]

            print "Displaying segment now...."
            cv2.namedWindow("Segment " + str(segment_counter))
            cv2.imshow("Segment " + str(segment_counter), roi)

            # Write the segment to a file so we can look at it later too.
            segment_file_name = "segments/s" + str(segment_counter) + "_" + image_file.replace(path, "").strip("/").strip("\\")
            if not os.path.exists("segments"):  # Create the "segments" directory if it does not exist yet.
               os.makedirs("segments")
            cv2.imwrite(segment_file_name, roi)

            # Use TensorFlow to classify the segment.
            object_name, score = run_inference_on_image(segment_file_name)
            print('%s (score = %.5f)' % (object_name, score))

            cv2.waitKey(0)  # Wait until the image is manually closed to continue.

            # Decide whether or not this is an unknown object.
            recognition_threshold = 0.9  # Subject to change.
            if score < recognition_threshold:  # If not recognized with a high probability, ask the user about this object and add a model for this object to the existing ImageNet model.
               name = learn_new_object.get_name()
               print name  # We can delete this line later; it's just useful for now to see what the program thinks the name is.

               # Determine whether this object is really unknown, and if so,
               # set a flag so the program will know to retrain its object and
               # attribute models with newly learned information once all (if
               # there are any additional) new objects are learned.
               is_really_new = learn_new_object.get_info(name)
               if is_really_new:
                  retrain_models = True

               # Add this name to the list of object names in the game space.
               object_names.append(name)
            else:  # Otherwise, add the name of this object to the list of recognized objects.
               object_names.append(object_name)

            segment_counter += 1
      # Show the original image with rectangles drawn on it.
      print "Displaying original image...."
      cv2.namedWindow("Original Image")
      cv2.imshow("Original Image", frame)
      cv2.imwrite("segments/" + image_file.replace(path, "").strip("/").strip("\\"), frame)
      cv2.waitKey(0)
   print "The following objects were found in the gamespace:\n", "\n".join(object_names)


if __name__ == '__main__':
   find_objects_alternate_seg()
