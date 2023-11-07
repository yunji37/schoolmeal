import cv2
from ultralytics import YOLO
import math
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import sort
import numpy as np
import subprocess
import threading
import queue

q=queue.Queue() # 데이터 추가/ 삭제
dirname = os.path.dirname(os.path.realpath(__file__)) # 현재 파일 경로

# W = 1920
# H = 1080

W = 1280
H = 720

command = [
    'ffmpeg',
    '-y',  # 기존 출력 파일을 덮어쓰기
    '-f', 'rawvideo', # !입력 형식을 원시 비디오로 지정
    '-vcodec', 'rawvideo', # !입력 비디오 코덱을 원시 비디오로 지정
    '-s', f'{W}x{H}',  # 해상도: 가로 x 세로
    '-pix_fmt', 'bgr24',  # OpenCV에서 사용하는 픽셀 형식
    '-i', '-',  # 표준 입력에서 비디오 데이터를 읽음
    '-an',  # 오디오 무시
    '-vcodec', 'libx264',  # 출력 비디오 코덱
    '-preset', 'ultrafast',  # 최대 속도를 위한 프리셋 사용
    '-tune', 'zerolatency',  # 제로 지연 튜닝 사용
    '-crf', '25',  # 압축 품질을 낮추어 빠른 변환 속도 얻기 (0-51 범위, 높은 값은 낮은 품질)
    '-f', 'hls', # !출력 형식을 HLS로 지정
    '-hls_flags', 'split_by_time', # !세그먼트를 시간 기준으로 분할
    '-hls_time', '1',  # 각 TS 파일의 길이(초)
    '-hls_list_size', '2', # !재생목록에 포함될 세그먼트의 최대 개수
    '-hls_flags', 'delete_segments',  # !재생목록에서 더 이상 필요하지 않은 세그먼트 삭제
    os.path.join(dirname, 'output', 'output.m3u8') # 출력 파일 경로
]

# ffmpeg 프로세스 생성
proc = subprocess.Popen(command, stdin=subprocess.PIPE)
model = YOLO(os.path.join(dirname, 'yolov8n.pt')) 

tracker = sort.Sort(max_age=20, min_hits=3, iou_threshold=0.3)
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
color = (255, 0, 0)
thickness = 2
log = {}
global cur
cur = 0
mask = cv2.imread('src/lib/images/mask.png')

def Receive():
    cap = cv2.VideoCapture("rtsp://admin1:rara2017!@172.30.1.57:554/stream1")
    cap.set(3, W) # 너비 설정 
    cap.set(4, H) # 높이 설정
    ret, frame = cap.read() # 프레임 읽기
    q.put(frame) # frame 데이터 삽입
    while ret: # 프레임 읽기가 정상이라면
        ret, frame = cap.read()
        q.put(frame)
    cap.release() # 메모리 해제

def Display():
    global cur # 전역변수 
    while True:
        if q.empty(): # q가 비어있으면 
            continue
        img = q.get() # 항목을 제거하고 반환
        # 마스크 이미지 적용
        img_region=cv2.bitwise_and(img,mask)

        results = model(img_region, stream=True, verbose=False) # img에 model 적용
        detections = np.empty((0,5)) # 배열 생성

        clsArr = []
        for r in results:
            boxes = r.boxes # 상자 표시 

            for box in boxes:
                # bounding box
                x1, y1, x2, y2 = map(int,box.xyxy[0])
                cls = int(box.cls[0])
                if cls != 0: continue

                # put box in cam
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # confidence
                confidence = math.ceil((box.conf[0]*100))/100

                # class name
                x = np.array([x1,y1,x2,y2,int(confidence * 100)])
                detections = np.vstack((detections, x))
                    
                # print("Class name -->", classNames[cls])
        
        # 영상 가운데 선
        cv2.line(img, (W // 2, 0),(W // 2, H), (0,0,255), 4)
        resultsTracker=tracker.update(detections)
        logkeys = set(log.keys())
        
        for r in resultsTracker:
            x1, y1, x2, y2, Id = r
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            if int(Id) in log:
                px, py = log[int(Id)]
                if px < W // 2 and cx > W // 2:
                    cur += 1
                elif px > W // 2 and cx < W // 2:
                    cur -= 1

            log[int(Id)] = (cx , cy)
            logkeys.discard(int(Id))

            cv2.putText( # bbox text
                img,
                f"person[{int(Id)}]",
                [int(x1), int(y1)],
                font,
                fontScale,
                color, 
                thickness
            )

        for l in logkeys:
            del log[l]

        cv2.putText( # 화면에 인식된 사람 수 
            img,
            f"{cur} {'person' if cur == 1 else 'people'}",
            [1100, 700],
            font,
            fontScale,
            (225, 225, 225),
            thickness
        )

        # ffmpeg에 프레임 쓰기
        proc.stdin.write(img.tobytes())
        if cv2.waitKey(1) == ord('q'):
            break

    proc.stdin.close()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    p1 = threading.Thread(target=Receive)
    p2 = threading.Thread(target=Display)
    p1.start()
    p2.start()