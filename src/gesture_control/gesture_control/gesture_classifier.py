import math

# 두 지점 사이의 거리 계산
def distance(a,b):
    return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)

# 손가락이 위로 펴져있는지 확인 (y는 작을 수록 위쪽)
def is_finger_up(landmarks, tip, pip):
    return landmarks[tip].y < landmarks[pip].y 

def recognize_gesture(hand_landmarks):
    lm = hand_landmarks

    # 엄지 up&down
    thumb_up = lm[4].y < lm[3].y
    thumb_down = lm[4].y > lm[3].y

    index_up = is_finger_up(lm,8,6) #검지 
    middle_up = is_finger_up(lm,12,10) #중지
    ring_up = is_finger_up(lm,16,14) #약지
    pinky_up = is_finger_up(lm,20,18) #새끼

    # 엄지-검지 거리 측정
    thumb_index_close = distance(lm[4], lm[8]) < 0.05

    # # 주먹: 모든 손가락이 접힘 -> 정지
    # if not any([thumb_up, index_up, middle_up, ring_up, pinky_up]):
    #     return 'stop'

    # # 앞을 가리킴: 검지만 펴짐 -> 직진
    # if index_up and not thumb_up and not middle_up and not ring_up and not pinky_up:
    #     return 'forward'

    # OK 제스처: 엄지-검지 거리 가깝고, 나머지 손가락 펴짐 -> 정지
    if thumb_index_close and middle_up and ring_up and pinky_up:
        return 'stop'

    # V자: 검지 + 중지 -> 직진
    if index_up and middle_up and not ring_up and not pinky_up:
        return 'forward'
    

    # 손바닥 펼치기: 모든 손가락이 펴짐 -> 후진
    if all([thumb_up, index_up, middle_up, ring_up, pinky_up]):
        return 'backward'


    # 오른쪽을 가리킴: 검지 손가락이 오른쪽을 가리킴-> 오른쪽으로 회전 후 이동
    # 왼쪽을 가리킴: 검지 손가락이 왼쪽을 가리킴 -> 왼쪽으로 회전 후 이동
    if lm[0].x < lm[8].x:
        return 'right'
    else:
        return 'left' 
    
    
    # 엄지로 위를 가리킴: 엄지만 위로 펴져있음 -> 속도 증가
    if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return 'speed_up'

    # 엄지로 아래를 가리킴: 엄지만 아래로 펴져있음 -> 속도 감소
    if thumb_down and not index_up and not middle_up and not ring_up and not pinky_up:
        return 'speed_down'
