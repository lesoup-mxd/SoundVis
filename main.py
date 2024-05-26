import os
import sys
import time
import tkinter as tk
import numpy as np
import cv2
from sklearn.cluster import KMeans


def fetch_dominant_colors(num_clusters=5):
    try:
        # Capture the screen
        os.popen("spectacle -f -n -b -o stream.png &> /dev/null").close()
        # Load the image using cv2.imread
        frame = cv2.imread(os.path.join(os.path.dirname(__file__), 'stream.png'))
        # Convert to RGB for K-means clustering
        # Resize frame for faster processing
        frame = cv2.resize(frame, (300, 300))
        # Flatten the frame
        pixels = frame.reshape(-1, 3)
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(pixels)
        # Get the RGB values of the cluster centers
        centers = kmeans.cluster_centers_
        return centers
    except KeyboardInterrupt:
        print("Program stopped.")
        sys.exit()

def create_window(color_num=5, height=300):
    root = tk.Tk()
    root.title("Dominant Colors")
    canvas = tk.Canvas(root, width=root.winfo_screenmmwidth(), height=300)
    canvas.pack()
    return root, canvas

def display_colors(colors, root, canvas):
    num_colors = len(colors)
    width_col = root.winfo_screenmmwidth() // num_colors
    for i, color in enumerate(colors):
        color = np.array(color, dtype=np.uint8)
        color = color.reshape(1, 1, 3)
        color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
        color = tuple(map(int, color[0][0]))
        canvas.create_rectangle(i*width_col, 0, (i+1)*width_col, 300, fill='#%02x%02x%02x' % color)
    # Run the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    def displayer():
        colors = fetch_dominant_colors()
        root, canvas = create_window()
        display_colors(colors, root, canvas)
    def led():
        colors = fetch_dominant_colors()
        import rgb
        import time
        rgb.connect()
        rgb.requestColorCorrected("ffffff")
        time.sleep(1)
        rgb.requestColorCorrected("000000")
        time.sleep(1)
        rgb.requestColorCorrected("ff0000")
        time.sleep(1)
        rgb.requestColorCorrected("00ff00")
        time.sleep(1)
        rgb.requestColorCorrected("0000ff")
        rgb.closeSerial()
    def print_colors():
        colors = fetch_dominant_colors()
        print(colors)
    displayer()
