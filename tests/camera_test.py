'''
camera_test.py
Created By: Peter Gish
Last Modified: 4/23/15
Accesses laptop camera and analyzes
each frame for straight lines
'''

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    minLineLength = 500
    maxLineGap = 20
    # fine lines in image
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)
    if lines is not None:
        for x1, y1, x2, y2 in lines[0]:
            # draw the line given by HoughLinesP method
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the capture
cap.release()
cv2.destroyAllWindows()
