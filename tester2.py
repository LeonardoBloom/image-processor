import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Function to calculate the energy map of an image
def calculate_energy(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate gradients using Sobel operator
    gradient_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # Calculate the energy map as the magnitude of the gradients
    energy_map = np.abs(gradient_x) + np.abs(gradient_y)
    return energy_map

# Function to find the optimal seam using dynamic programming
def find_vertical_seam(energy_map):
    rows, cols = energy_map.shape
    seam_energy = energy_map.copy()
    
    # Populate the seam energy matrix with the cumulative minimum energy
    for i in range(1, rows):
        for j in range(cols):
            if j == 0:
                min_energy = min(seam_energy[i-1, j], seam_energy[i-1, j+1])
            elif j == cols - 1:
                min_energy = min(seam_energy[i-1, j-1], seam_energy[i-1, j])
            else:
                min_energy = min(seam_energy[i-1, j-1], seam_energy[i-1, j], seam_energy[i-1, j+1])
            seam_energy[i, j] += min_energy
    
    # Backtrack to find the seam path
    seam = []
    j = np.argmin(seam_energy[-1])
    seam.append((rows-1, j))
    
    for i in range(rows-2, -1, -1):
        if j > 0 and j < cols-1:
            j = j + np.argmin([seam_energy[i, j-1], seam_energy[i, j], seam_energy[i, j+1]]) - 1
        elif j == 0:
            j = np.argmin([seam_energy[i, j], seam_energy[i, j+1]])
        else:
            j = j + np.argmin([seam_energy[i, j-1], seam_energy[i, j]]) - 1
        seam.append((i, j))
    
    seam.reverse()
    return seam

# Function to remove the seam from the image
def remove_seam(img, seam):
    rows, cols, _ = img.shape
    for row, col in seam:
        img[row, col:cols-1] = img[row, col+1:cols]
    img = img[:, :-1]  # Remove last column
    return img

# Function to apply the seam carving
def apply_seam_carving(img, num_seams):
    for _ in range(num_seams):
        energy_map = calculate_energy(img)
        seam = find_vertical_seam(energy_map)
        img = remove_seam(img, seam)
    return img

# GUI setup
root = tk.Tk()
root.title("Content-Dependent Image Warping")

# Function to load image
def load_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        img = cv2.imread(file_path)
        global loaded_img
        loaded_img = img.copy()  # Keep a copy of the loaded image
        show_image(loaded_img, panel_original)

def show_image(img, panel):
    # Convert BGR to RGB for displaying with PIL
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)
    
    panel.config(image=img_tk)
    panel.image = img_tk

# Function to apply warping (seam carving)
def apply_warping():
    global loaded_img
    # Ask the user for the number of seams to remove
    num_seams = int(num_seams_entry.get())
    if num_seams > 0:
        warped_img = apply_seam_carving(loaded_img, num_seams)
        show_image(warped_img, panel_warped)

# GUI layout
panel_original = tk.Label(root)
panel_original.grid(row=0, column=0)

panel_warped = tk.Label(root)
panel_warped.grid(row=0, column=1)

btn_load = tk.Button(root, text="Load Image", command=load_image)
btn_load.grid(row=1, column=0)

tk.Label(root, text="Number of seams to remove:").grid(row=1, column=1)
num_seams_entry = tk.Entry(root)
num_seams_entry.grid(row=1, column=2)

btn_warp = tk.Button(root, text="Warp Image", command=apply_warping)
btn_warp.grid(row=2, column=1)

root.mainloop()
