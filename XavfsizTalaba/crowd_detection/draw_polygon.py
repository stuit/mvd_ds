import cv2
import numpy as np

points = []
points_percent = []
screen = None

def get_coordinates(event, x, y, flags, param):
    global points, points_percent, screen
    if event == cv2.EVENT_LBUTTONDOWN:
        if screen is not None:
            h, w, c = screen.shape
            x_per, y_per = x / w, y / h
            points_percent.append([round(x_per,3), round(y_per,3)])
            points.append([x, y])
            print(f"Point captured: ({x}, {y})")
            print(points_percent)
            print(points)
        else:
            print("Screen is not set yet.")

def draw_polylines(frame, points):
    global screen
    screen = frame.copy()
    if len(points) > 1:
        cv2.polylines(frame, [np.array(points, dtype=np.int32)], isClosed=False, color=(0, 255, 0), thickness=2)
    for point in points:
        cv2.circle(frame, point, 5, (0, 0, 255), -1)

stream_url = '/Users/abduqayumrasulmuhamedov/Desktop/fight_detection_project/test_videos/IPC_20250430160908 (1).avi'
cap = cv2.VideoCapture(stream_url)

cv2.namedWindow('Stream')
cv2.setMouseCallback('Stream', get_coordinates)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.resize(frame, (1080, 720))
    draw_polylines(frame, points)
    cv2.imshow('Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("Points:", points)
print("Points percent:", points_percent)