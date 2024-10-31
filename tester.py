import os

folder_in = 'in'
folder_out = 'out'

filename_input = 'imageTest.jpg'
filename_output = 'image_result.png'
filename_mask = 'mask.jpg'
new_height = 200
new_width = 512

input_image = os.path.join(folder_in, "images", filename_input)
input_mask = os.path.join(folder_in, "masks", filename_mask)
output_image = os.path.join(folder_out, "images", filename_output)

print(input_image)
print(output_image)

