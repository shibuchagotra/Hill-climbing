import cv2
from pynput.keyboard import Controller, Key
from mediapipe.python.solutions import hands
# Create objects
hand = hands.Hands()
keyboard = Controller()

# Tips Id
tipIds = [4, 8, 12, 16, 20]

# Functions to find hands in image
def findHands(img, flipType=True):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hand.process(imgRGB)
    allHands = []
    h, w, c = img.shape
    if results.multi_hand_landmarks:
        for handType, handLms in zip(results.multi_handedness, results.multi_hand_landmarks):
            myHand = {}
            # lmList
            mylmList = []
            xList = []
            yList = []
            for id, lm in enumerate(handLms.landmark):
                px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                mylmList.append([px, py, pz])
                xList.append(px)
                yList.append(py)

            # Bounding box
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            boxW, boxH = xmax - xmin, ymax - ymin
            bbox = xmin, ymin, boxW, boxH
            cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2)

            myHand["lmList"] = mylmList
            myHand["bbox"] = bbox
            myHand["center"] = (cx, cy)

            if flipType:
                if handType.classification[0].label == "Right":
                    myHand["type"] = "Left"
                else:
                    myHand["type"] = "Right"
            else:
                myHand["type"] = handType.classification[0].label
            allHands.append(myHand)
    return allHands, img, results

# Function to count fingers
def fingersUp(results, myHand):
    fingers = []
    myHandType = myHand["type"]
    myLmList = myHand["lmList"]
    if results.multi_hand_landmarks:
        # Thumb
        if myHandType == "Right":
            if myLmList[tipIds[0]][0] > myLmList[tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if myLmList[tipIds[0]][0] < myLmList[tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if myLmList[tipIds[id]][1] < myLmList[tipIds[id] - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)
    return fingers

# Brake function
def Brake(lmList2):
    l2 = fingersUp(results, lmList2)
    return l2

# Gas function
def Gas(lmList1):
    l1 = fingersUp(results, lmList1)
    return l1

# Capture video
cap = cv2.VideoCapture(0)
# Declaration
counter = 0
l1=[]
l2=[]

while True:
    _, img = cap.read()
    hands, img, results = findHands(img, flipType=True)

    if len(hands) == 2:

        if hands[0]['type'] == 'Left' and hands[1]['type'] == 'Right':
            l1 = Gas(hands[1])  # Right hand controls gas
            l2 = Brake(hands[0])  # Left hand controls brake
        elif hands[0]['type'] == 'Right' and hands[1]['type'] == 'Left':
            l1 = Gas(hands[0])  # Right hand controls gas
            l2 = Brake(hands[1])  # Left hand controls brake

        if l1.count(1) == 5 and l2.count(1) == 0:
            keyboard.press(Key.right)
            keyboard.release(Key.left)
          
        if l2.count(1) == 5 and l1.count(1) == 0:
            keyboard.press(Key.left)
            keyboard.release(Key.right)
            
        if l2.count(1) == 0 and l1.count(1) == 0:
            keyboard.release(Key.right)
            keyboard.release(Key.left)
    else:
        keyboard.release(Key.right)
        keyboard.release(Key.left)
    counter += 1
    img=cv2.flip(img,1)
    cv2.imshow("IMG", img)
    if counter == 11:
        counter = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
