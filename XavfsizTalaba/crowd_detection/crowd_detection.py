import cv2
import numpy as np
import time
from ultralytics import YOLO
from shapely.geometry import Point, Polygon
from collections import deque

model = YOLO('yolov8s.pt')

polygon_points = [[5, 306], [978, 311], [1009, 696], [3, 709]]

polygon = Polygon(polygon_points)

crowd_threshold = 8  
frame_queue = deque()
average_duration = 10 
frame_interval = 3  

def is_in_polygon(x, y):
    point = Point(x, y)
    return polygon.contains(point)

# specify video path
cap = cv2.VideoCapture("test_videos/IPC_20250430160908 (1).avi")
frame_count = 0
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fourcc = cv2.VideoWriter_fourcc(*"h264")
# specify saved video path
videowriter = cv2.VideoWriter("test_results/test_crowd.mp4", fourcc, 20.0, (int(width), int(height)))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_interval != 0:  
        continue  

    results = model.predict(frame, conf=0.3, iou=0.4, classes=0, verbose=False)  

    count_in_polygon = 0  

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  

            if is_in_polygon(cx, cy):
                count_in_polygon += 1
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    frame_queue.append((count_in_polygon, time.time()))

    while len(frame_queue) > 0 and (time.time() - frame_queue[0][1] > average_duration):
        frame_queue.popleft()

    if len(frame_queue) > 0:
        average_count = np.mean([count for count, _ in frame_queue])
    else:
        average_count = 0

    cv2.polylines(frame, [np.array(polygon_points)], isClosed=True, color=(255, 0, 0), thickness=2)

    cv2.putText(frame, f'People Count: {count_in_polygon}', (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Average Count: {average_count:.2f}', (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Crowd Threshold: {crowd_threshold}', (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Time Period: {average_duration}s', (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    if average_count >= crowd_threshold:
        cv2.putText(frame, 'Crowd Detected!', (10, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('Crowd Detection', frame)
    videowriter.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

videowriter.release()
cap.release()
cv2.destroyAllWindows()
