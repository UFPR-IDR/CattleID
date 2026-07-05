""" Implements out of the box matching functions.

    This file references the legacy/matcher/sift_matcher.py file in the legacy code.
"""
import cv2
import ntpath
import numpy as np
import matplotlib.pyplot as plt

from utils import bwmorph


def img_keypoints(img_path: str, opencv_kp_format: bool = False, debug: bool = False):
    """ Gets the keypoints from an image.

    Arguments:
    img_path: Path to the image.
    opencv_kp_format: Boolean indicating if format should be kept.
    debug: Variable to define debug prints.

    Returns:
    list: Contains the binary image's keypoints.
    """
    img = cv2.imread(img_path, 0)
    if debug:
        print("shape: %s  |  max: %d  |  min: %d" % (img.shape, img.max(), img.min()))

    img_neighbors = bwmorph._neighbors_conv(img==255)

    # Adapt list of [x,y] to use with OpenCV
    vertices_pixel_list = np.transpose(np.where(img_neighbors>2)) # Returning a numpy array
    vertices_pixel_list = vertices_pixel_list.tolist()
    
    if debug:
        print(f"Before clean: {len(vertices_pixel_list)}")
        for i in range(10):
            print(vertices_pixel_list[i])
    
    # Clean coupled pixels
    for px in vertices_pixel_list:
        for i in range(-2, 2):
            for j in range(-2, 2):
                aux = [px[0] + i, px[1] + j]
                if aux in vertices_pixel_list and aux != px:
                    vertices_pixel_list.remove(aux)

    if debug:
        print(f"After clean: {len(vertices_pixel_list)}")
        for i in range(10):
            print(vertices_pixel_list[i])

        
    # Make image w/ highlighted vertices
    if debug:   
        img_bgr = np.stack((img,)*3, axis=-1)  # Changing from mono to bgr (copying content to all channels)
        for px in vertices_pixel_list:
            img_bgr[px[1], px[0]] = (0,0,255)  # Red. OpenCV uses BGR
        cv2.imwrite("vertexestup.png", img_bgr)

    # Converts list of tuples (X,Y) to Keypoints
    if(opencv_kp_format):
        vertices_pixel_tuple = [(y, x) for x, y in vertices_pixel_list]
        cv_keyPoints = cv2.KeyPoint_convert(vertices_pixel_tuple)
        return cv_keyPoints
    else:
        return [[y, x] for x, y in vertices_pixel_list]
    

def sift_brute_compare(img_path1: str, img_path2: str, img_roi1: str, img_roi2: str, save_path: str, debug: bool = False):
    """ Compare keypoints between two images using bruteforce.

    References: https://docs.opencv.org/3.4/d5/dde/tutorial_feature_description.html (adapted to SIFT)

    Arguments:
    img_path1: The path to an image.
    img_path2: The path to an image.
    img_roi1: The path to an ROI.
    img_roi2: The path to an ROW.
    save_path: The path to save the comparison.
    debug: Variable indicating if the function is in debug mode.    
    """
    sift = cv2.SIFT_create()
    
    # Loads the images
    img1 = cv2.imread(img_path1)
    img2 = cv2.imread(img_path2)
    roi1 = cv2.imread(img_roi1)
    roi2 = cv2.imread(img_roi2)

    # Calculates vertices (keypoints) of images
    keypoints1 = img_keypoints(img_path1, opencv_kp_format=True)    
    keypoints2 = img_keypoints(img_path2, opencv_kp_format=True)    

    # Visualize keypoints calculated
    if debug:
        gray= cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        image = cv2.drawKeypoints(gray, keypoints1, img1)
        cv2.imwrite("vertices_debug.png", image)

    # Detect the keypoints using SIFT Detector, compute the descriptors
    keypoints1, descriptors1 = sift.compute(roi1, keypoints1)
    keypoints2, descriptors2 = sift.compute(roi2, keypoints2)

    # TODO: implement RANSAC, this is using brute force
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE)
    matches = matcher.match(descriptors1, descriptors2)

    # Draw matches
    img_matches = np.empty((max(img1.shape[0], img2.shape[0]), img1.shape[1]+img2.shape[1], 3), dtype=np.uint8)
    cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches, img_matches)

    # Save name of matched files
    name1 = ntpath.basename(img_path1)
    name2 = ntpath.basename(img_path2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_matches,name1,(0,img1.shape[0]-10), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    cv2.putText(img_matches,name2,(img1.shape[1],img2.shape[0]-10), font, 0.5,(255,255,255),1,cv2.LINE_AA)

    # Saves detected matches
    cv2.imwrite(save_path, img_matches)


def sift_knn_compare(img_path1: str, img_path2: str, img_roi1: str, img_roi2: str, save_path: str, debug: bool = False):
    """ Compare keypoints between two images using KNN.

    References: https://docs.opencv.org/3.4/d5/dde/tutorial_feature_description.html (adapted to SIFT)

    Arguments:
    img_path1: The path to an image.
    img_path2: The path to an image.
    img_roi1: The path to an ROI.
    img_roi2: The path to an ROW.
    save_path: The path to save the comparison.
    debug: Variable indicating if the function is in debug mode.    
    """
    sift = cv2.SIFT_create()
    
    # Loads the images
    img1 = cv2.imread(img_path1)
    img2 = cv2.imread(img_path2)
    roi1 = cv2.imread(img_roi1)
    roi2 = cv2.imread(img_roi2)

    # Calculates vertices (keypoints) of images
    keypoints1 = img_keypoints(img_path1, opencv_kp_format=True)    
    keypoints2 = img_keypoints(img_path2, opencv_kp_format=True)    

    # Visualize keypoints calculated
    if debug:
        gray= cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        image = cv2.drawKeypoints(gray, keypoints1, img1)
        cv2.imwrite("vertices_debug.png", image)

    # Detect the keypoints using SIFT Detector, compute the descriptors
    keypoints1, descriptors1 = sift.compute(roi1, keypoints1)
    keypoints2, descriptors2 = sift.compute(roi2, keypoints2)

    matcher = cv2.BFMatcher()
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

    good = []
    for m, n in matches:
        if m.distance < 1*n.distance: # Default is .75
            good.append([m])

    #  Draw matches
    img_matches = cv2.drawMatchesKnn(img1, keypoints1, img2, keypoints2, good, None, flags=2)

    # Save name of matched files
    name1 = ntpath.basename(img_path1)
    name2 = ntpath.basename(img_path2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_matches,name1,(0,img1.shape[0]-10), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    cv2.putText(img_matches,name2,(img1.shape[1],img2.shape[0]-10), font, 0.5,(255,255,255),1,cv2.LINE_AA)

    # Save detected matches
    cv2.imwrite(save_path , img_matches)


def flann_compare(img_path1: str, img_path2: str):
    """ Compare keypoints between two images using flann.

    References: https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html

    Arguments:
    img_path1: The path to an image.
    img_path2: The path to an image.
    """
    MIN_MATCH_COUNT = 10
    sift = cv2.SIFT_create()
    
    # Loads the images
    img1 = cv2.imread(img_path1, 0)
    img2 = cv2.imread(img_path2, 0)

    # Calculates vertices (keypoints) of images
    kp1 = img_keypoints(img_path1, opencv_kp_format=True)    
    kp2 = img_keypoints(img_path2, opencv_kp_format=True)    

    # Detect the keypoints using SIFT Detector, compute the descriptors
    kp1, des1 = sift.compute(img1, kp1)
    kp2, des2 = sift.compute(img2, kp2)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    # Store all the good matches as per Lowe's ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
            
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()
        h, w = img1.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        img2 = cv2.polylines(img2,[np.int_32(dst)],True,255,3, cv2.LINE_AA)
    else:
        print("Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))
        matchesMask = None
        
    # Draw inliners if success OR keypoints if failed
    draw_params = dict(matchColor = (0,255,0), # Draw matches in green color
                       singlePointColor = None,
                       matchesMask = matchesMask, # Draw only inliers
                       flags = 2)
    output = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
    plt.imshow(output, "gray")
    plt.show()


def blob_visualize(img_path1: str, img_roi: str, save_path: str, use_key_points: bool = True):
    """ Plots a blob image.

    References:https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html

    Arguments:
    img_path1: The path to an image.
    img_roi: The path to an ROI.
    save_path: Path to save the image.
    use_key_points: Defines wheter to use the generated keypoints.
    """
    sift = cv2.SIFT_create()

    roi_img = cv2.imread(img_roi)
    roi_img = cv2.resize(roi_img, (512, 512))
    gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
    
    # Keypoints default/extracted from binary Image
    if(use_key_points):
        keypts = img_keypoints(img_path1, opencv_kp_format=True)
        keypts, _ = sift.compute(roi_img, keypts)
    else:
        keypts, _ = sift.detectAndCompute(gray, None)

    roi_img = cv2.drawKeypoints(gray, keypts, roi_img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imwrite(save_path, roi_img)    
