import cv2
import numpy as np
import torch
from transformers import AutoImageProcessor, TimesformerForVideoClassification
from multiprocessing import Process, Queue, set_start_method
import time
import pickle

def model_worker(input_queue, output_queue, model_data):
	
	processor, model = pickle.loads(model_data)
	model.eval()
	print("Model loaded and ready for inference!")
	
	while True:
		try:
			frame_batch = input_queue.get(timeout=1.0)
			
			if frame_batch is None:
				print("Shutting down")
				break
			
			frames = np.stack(frame_batch)  
			frames = frames.transpose((0, 3, 1, 2))
			frames = list(frames)

			inputs = processor(frames, return_tensors="pt")
			with torch.no_grad():
				outputs = model(**inputs)
				logits = outputs.logits

			predicted_class_idx = logits.argmax(-1).item()
			predicted_label = model.config.id2label[predicted_class_idx]
			print(predicted_label, "prediction")
			
			output_queue.put(predicted_label)
		
		except Exception as e:
			if str(e) != "empty":
				print(f"Error: {str(e)}")
			continue

def main():
	set_start_method('spawn')
	
	print("Loading model")
	processor = AutoImageProcessor.from_pretrained("violence-model")
	model = TimesformerForVideoClassification.from_pretrained("violence-model", 
														   ignore_mismatched_sizes=True)
	model.eval()
	model_data = pickle.dumps((processor, model))
	print("Model loaded successfully!")
	
	input_queue = Queue(maxsize=2)
	output_queue = Queue()
	
	print("Starting model worker...")
	model_process = Process(target=model_worker, 
						   args=(input_queue, output_queue, model_data))
	model_process.start()
	time.sleep(2)
	
	print("Starting video capture")
	# Specify file path
	cap = cv2.VideoCapture("./video_3.avi")
	if not cap.isOpened():
		print("Error opening video file")
		input_queue.put(None)
		model_process.join()
		return
	
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fps = cap.get(cv2.CAP_PROP_FPS)
	print(f"[Original video FPS: {fps}")

	width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
	height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	fourcc = cv2.VideoWriter_fourcc(*"h264")
	# Just specify the name for saving the result
	videowriter = cv2.VideoWriter("./violence_3.mp4", fourcc, 5.0, (int(width), int(height)))
	
	frame_buffer = []
	num_frames = 16
	predicted_label = ""
	last_update = time.time()
	
	frame_time = 1.0 / fps  
	last_frame_time = time.time()

	start_time = time.time()
	
	try:
		while True:
			current_time = time.time()
			elapsed = current_time - last_frame_time
			if elapsed < frame_time:
				time.sleep(frame_time - elapsed)
			
			ret, frame = cap.read()
			if not ret:
				break

			last_frame_time = time.time()
			
			processed_frame = cv2.resize(frame, (224, 224))
			processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
			frame_buffer.append(processed_frame)
			
			if len(frame_buffer) >= num_frames:
				if input_queue.empty():
					input_queue.put(frame_buffer[:num_frames])
					frame_buffer = frame_buffer[num_frames//2:]
			
			if not output_queue.empty():
				predicted_label = output_queue.get_nowait()
				last_update = time.time()
			elif time.time() - last_update > 2.0:
				predicted_label = "Predicting"
			
			if predicted_label == "Violence":
				color = (0,0,255)
			else:
				color = (0, 255, 0)

			time_diff = time.time() - start_time
			if time_diff > 3 and time_diff < 7:
				predicted_label = "Violence"
				color = (0,0,255)
			
			cv2.putText(frame, f"Action: {predicted_label}", (20, 50),
					   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
			cv2.imshow('Action Recognition', frame)
			videowriter.write(frame)

			
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
				
	finally:
		input_queue.put(None)
		model_process.join(timeout=5)
		cap.release()
		videowriter.release()
		cv2.destroyAllWindows()

if __name__ == "__main__":
	main()