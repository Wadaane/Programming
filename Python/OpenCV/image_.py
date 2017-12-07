import cv2
from matplotlib import pyplot as plt

img = cv2.imread('messi5.jpg', 0)

# Show image in matplotlib
plt.imshow(img, cmap='gray', interpolation='bicubic')
plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
plt.show()

k = cv2.waitKey(0)
if k == 27:  # wait for ESC key to exit
    cv2.destroyAllWindows()
