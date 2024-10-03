import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import Canvas

#OpenCV
cap = cv2.VideoCapture(0)

def count_fingers(thresholded, segmented):
    contours, _ = cv2.findContours(thresholded.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return 0

    contour = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(contour, returnPoints=False)

    if len(hull) < 4:
        return 0

    defects = cv2.convexityDefects(contour, hull)

    if defects is None:
        return 0

    finger_count = 0
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contour[s][0])
        end = tuple(contour[e][0])
        far = tuple(contour[f][0])

        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57.2958

        if angle <= 90:
            finger_count += 1

    return finger_count + 1

root = tk.Tk()
root.title("Pong with Finger Control")

WIDTH, HEIGHT = 640, 480
canvas = Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()

#Game Variables
paddle_width, paddle_height = 10, 100
ball_radius = 7
ball_speed_x, ball_speed_y = 5, 5
paddle_speed = 7

#Paddle and Ball Position
player_paddle_y = HEIGHT // 2 - paddle_height // 2
computer_paddle_y = HEIGHT // 2 - paddle_height // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2

#Scores
player_score = 0
computer_score = 0

FPS = 60

def update_game():
    global player_paddle_y, computer_paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y
    global player_score, computer_score

    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        root.after(100, update_game)
        return

    frame = cv2.flip(frame, 1)
    roi = frame[100:400, 100:400]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (35, 35), 0)
    _, thresholded = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresholded.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    fingers = 0
    if len(contours) > 0:
        segmented = max(contours, key=cv2.contourArea)
        fingers = count_fingers(thresholded, segmented)

    print(f"Fingers detected: {fingers}")  # Debugging output

    #Move Player Paddle
    if fingers == 5:
        player_paddle_y -= paddle_speed
    elif fingers == 4:
        player_paddle_y += paddle_speed

    #Ensure player paddle stays within the screen bounds
    player_paddle_y = max(0, min(HEIGHT - paddle_height, player_paddle_y))

    # Move Ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    #Ball collision with top and bottom walls
    if ball_y - ball_radius < 0 or ball_y + ball_radius > HEIGHT:
        ball_speed_y *= -1

    #Ball collision with paddles
    if ball_x - ball_radius < paddle_width and player_paddle_y < ball_y < player_paddle_y + paddle_height:
        ball_speed_x *= -1
    elif ball_x + ball_radius > WIDTH - paddle_width and computer_paddle_y < ball_y < computer_paddle_y + paddle_height:
        ball_speed_x *= -1

    #Ball out of bounds
    if ball_x - ball_radius < 0:
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Reset ball to the center
        ball_speed_x *= -1  # Change direction of ball
        computer_score += 1  # Increase computer score
    elif ball_x + ball_radius > WIDTH:
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Reset ball to the center
        ball_speed_x *= -1  # Change direction of ball
        player_score += 1  # Increase player score

    #Here is the "player 2 paddle" nothing too fancy, you can make your own AI if you want
    if computer_paddle_y + paddle_height / 2 < ball_y:
        computer_paddle_y += paddle_speed / 2
    elif computer_paddle_y + paddle_height / 2 > ball_y:
        computer_paddle_y -= paddle_speed / 2

    #Ensure computer paddle stays within the screen bounds
    computer_paddle_y = max(0, min(HEIGHT - paddle_height, computer_paddle_y))

    canvas.delete("all")
    canvas.create_rectangle(0, player_paddle_y, paddle_width, player_paddle_y + paddle_height, fill='white')
    canvas.create_rectangle(WIDTH - paddle_width, computer_paddle_y, WIDTH, computer_paddle_y + paddle_height, fill='white')
    canvas.create_oval(ball_x - ball_radius, ball_y - ball_radius, ball_x + ball_radius, ball_y + ball_radius, fill='white')

    #Scores
    canvas.create_text(WIDTH // 4, 20, text=f"Player: {player_score}", fill='white', font=('Arial', 20))
    canvas.create_text(3 * WIDTH // 4, 20, text=f"Computer: {computer_score}", fill='white', font=('Arial', 20))

    #OpenCV windows (for debugging)
    cv2.imshow('ROI', roi)
    cv2.imshow('Thresholded', thresholded)
    cv2.waitKey(1)

    #Next update
    root.after(int(1000 / FPS), update_game)

#Start the game loop
update_game()
root.mainloop()

#This just clean up
cap.release()
cv2.destroyAllWindows()
