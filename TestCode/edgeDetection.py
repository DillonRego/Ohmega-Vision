import cv2


class Edge_Detection:
  
    def __init__(self, imgName):
        self.img = cv2.imread(imgName)

    # Blur the image for better edge detection
    def blur(self):
        # Convert to graycsale
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.img_blur = cv2.GaussianBlur(img_gray, (3,3), 0)
        return self.img_blur
        
    # Sobel Edge Detection on the X axis
    def sobelx(self):
        return cv2.Sobel(src=self.img_blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5) 

    # Sobel Edge Detection on the Y axis
    def sobely(self):
        return cv2.Sobel(src=self.img_blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5) 

    # Combined X and Y Sobel Edge Detection
    def sobelxy(self):
        return cv2.Sobel(src=self.img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5) 
        
    # Canny Edge Detection
    def canny(self):
        return cv2.Canny(image=self.img_blur, threshold1=100, threshold2=200)
    
    # Display img in a window  
    def showImage(self, img_name, image):
        cv2.imshow(img_name, image)
        cv2.waitKey(0)        
        
        
def main():
    # Read the original image
    edge = Edge_Detection('Sample2.jpg')

    edge.showImage('Original', edge.img)

    edge.blur()
    sobelx = edge.sobelx()
    edge.showImage('Sobel X', sobelx)
    sobely = edge.sobely()
    edge.showImage('Sobel Y', sobely)
    sobelxy = edge.sobelxy()
    edge.showImage('Sobel X Y', sobelxy)
    canny = edge.canny()
    edge.showImage('Canny Edge Detection', canny)
 
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()   
