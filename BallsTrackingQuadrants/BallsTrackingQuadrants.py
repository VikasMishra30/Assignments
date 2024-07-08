import cv2
import numpy as np
import time

time_yellow, time_orange, time_green, time_white = [], [], [], []
quad_yellow, quad_orange, quad_green, quad_white = [], [], [], []

f = open("event_log.txt", "w")

colors = ["yellow", "orange", "green", "white"]

def quad(x, y):
    if 1260 < x < 1740 and 540 < y < 1000:
        return 1
    elif 790 < x < 1215 and 540 < y < 1010:
        return 2
    elif 800 < x < 1222 and 30 < y < 500:
        return 3
    elif 1260 < x < 1740 and 30 < y < 500:
        return 4
    return None

cap = cv2.VideoCapture('C:\Study\CSE\Projects\Assignment\BallTrackQuad\AIAssignmentVideo.mp4')

start = time.time()
entry_time = {color: None for color in colors}
exit_time = {color: None for color in colors}
ball_present = {color: False for color in colors}
annotations = []

while cap.isOpened():
    ret, frame = cap.read()
    cv2.namedWindow("Ball Tracking", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Ball Tracking", 1280, 720)

    if ret:
        # Convert to grayscale and apply Gaussian blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (17, 17), 0)

        # Detect circles
        circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1.4, 90, param1=100, param2=35, minRadius=10, maxRadius=80)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for (x, y, rad) in circles[0, :]:
                cv2.circle(frame, (x, y), rad, (100, 255, 0), 3)
                b, g, r = frame[y, x]

                # Detect color of the ball
                color_detected = None
                if 57 < r < 213 and 52 < g < 189 and 15 < b < 63:
                    color_detected = "yellow"
                elif 12 < r < 55 and 41 < g < 77 and 34 < b < 69:
                    color_detected = "green"
                elif 176 < r < 255 and 61 < g < 167 and 29 < b < 131:
                    color_detected = "orange"
                elif 113 < r < 248 and 111 < g < 246 and 94 < b < 226:
                    color_detected = "white"

                if color_detected:
                    quad_num = quad(x, y)
                    end_time = time.time()
                    time_in = end_time - start
                    event_time = int(time_in)

                    if color_detected == "yellow":
                        quad_yellow.append(quad_num)
                        time_yellow.append(event_time)
                    elif color_detected == "green":
                        quad_green.append(quad_num)
                        time_green.append(event_time)
                    elif color_detected == "orange":
                        quad_orange.append(quad_num)
                        time_orange.append(event_time)
                    elif color_detected == "white":
                        quad_white.append(quad_num)
                        time_white.append(event_time)

                    if entry_time[color_detected] is None:
                        entry_time[color_detected] = time.time()
                        f.write(f"{event_time}, {quad_num}, {color_detected}, Entry\n")
                        annotations.append((time.time(), f"{color_detected} entered at {event_time}s in quadrant {quad_num}"))
                        ball_present[color_detected] = True
                    else:
                        if time.time() - entry_time[color_detected] > 1.5:
                            entry_time[color_detected] = None
                            f.write(f"{event_time}, {quad_num}, {color_detected}, Exit\n")
                            annotations.append((time.time(), f"{color_detected} exited at {event_time}s in quadrant {quad_num}"))
                            exit_time[color_detected] = time.time()
                            ball_present[color_detected] = False

                    cv2.putText(frame, f"{color_detected} ({quad_num})", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Display entry and exit annotations on the left side of the frame
        current_time = time.time()
        y_offset = 30
        for timestamp, text in annotations:
            if current_time - timestamp < 1.5:
                cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_offset += 30
            else:
                annotations.remove((timestamp, text))

        cv2.imshow('Ball Tracking', frame)
        
        # Exit if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
f.close()