import time
import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Conexões oficiais dos 33 pontos do MediaPipe Pose
POSE_CONNECTIONS = [
    # Rosto
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
    # Tronco
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Braço Esquerdo
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    # Braço Direito
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    # Perna Esquerda
    (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
    # Perna Direita
    (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
]

options = PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="/home/andrey/Downloads/Atema/motionfit/pose_landmarker_full.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_poses=1,
)

webcam = cv2.VideoCapture(0)

if webcam.isOpened():
    with PoseLandmarker.create_from_options(options) as landmarker:
        
        while True:
            validacao, frame = webcam.read()

            if not validacao:
                break

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp_ms = int(time.time() * 1000)
            results = landmarker.detect_for_video(mp_image, timestamp_ms)

            if results.pose_landmarks:
                for pose_landmarks in results.pose_landmarks:
                    
                    # 1. Desenhar as linhas de conexão
                    for start_idx, end_idx in POSE_CONNECTIONS:
                        if start_idx < len(pose_landmarks) and end_idx < len(pose_landmarks):
                            s = pose_landmarks[start_idx]
                            e = pose_landmarks[end_idx]

                            sx, sy = int(s.x * w), int(s.y * h)
                            ex, ey = int(e.x * w), int(e.y * h)

                            cv2.line(frame, (sx, sy), (ex, ey), (0, 128, 255), 2)

                    # 2. Desenhar os pontos das articulações
                    for landmark in pose_landmarks:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            cv2.imshow("Webcam", frame)

            key = cv2.waitKey(5)
            if key == 27:  # Pressione ESC para sair
                break

        cv2.imwrite("frame.jpg", frame)

webcam.release()
cv2.destroyAllWindows()