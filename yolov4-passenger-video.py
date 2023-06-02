import cv2
import numpy as np
# import DeviceManager

MAX_PASSENGER_NUM = 9


# YOLOv4 모델과 가중치 파일 경로
model_path = "yolov4-passenger-tiny_last.weights"
config_path = "yolov4-passenger-tiny.cfg"

# YOLOv4 모델 로드
# net = cv2.dnn.readNetFromDarknet(config_path, model_path)
# or
net = cv2.dnn.readNet(model_path, config_path)
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

# GPU를 사용할 경우
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# 클래스 이름
classes = ["passenger"]

# 이미지 파일 경로

# 웹캠으로부터 입력 받기 위해 VideoCapture 객체 생성
cap = cv2.VideoCapture(0)
# 웹캠 프레임 사이즈 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

cv2.namedWindow("YOLOv4-passenger", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("YOLOv4-passenger", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


while True:
    # 웹캠에서 프레임 읽어오기
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (224, 224))

    # 이미지 크기 가져오기
    height, width = frame.shape[:2]

    # 이미지를 YOLOv4 모델 입력 크기에 맞게 리사이징
    scale = 1 / 255.0
    size = (224, 224)
    blob = cv2.dnn.blobFromImage(frame, scale, size, swapRB=True, crop=False)

    # YOLOv4 모델에 이미지 입력
    net.setInput(blob)

    # YOLOv4 모델 실행
    output_layers_names = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers_names)

    # 감지된 객체를 저장할 리스트 초기화
    boxes = []
    confidences = []
    class_ids = []

    # 감지된 객체 정보 추출
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # NMS(Normalized Maximum Suppression) 적용
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.5)

    frame = cv2.resize(frame, (480, 320))
    x_scale = 480.0/224.0
    y_scale = 320.0/224.0


    if len(indexes) > 0:
        passengerAreaClor = (0, 0, 255)
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            x = int(x*x_scale)
            y = int(y*y_scale)
            w = int(w*x_scale)
            h = int(h*y_scale)

            color = (0, 255, 128)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            text = f"{classes[class_ids[i]]}: {confidences[i]:.2f}"
            cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 결과 이미지 출력
    frame = cv2.resize(frame, (480, 320))
    cv2.putText(frame, "passenger", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, "{}/{} ({})".format(len(indexes), MAX_PASSENGER_NUM, MAX_PASSENGER_NUM-len(indexes)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow("YOLOv4-passenger", frame)
    if cv2.waitKey(1) == ord("q"):
        break

