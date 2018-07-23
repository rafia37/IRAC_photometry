import numpy as np
import matplotlib.pyplot as plt
import sys, pdb, glob
from photutils import CircularAperture, CircularAnnulus, aperture_photometry
from astropy.io import fits, ascii
from astropy.table import Table, Column
from astropy.modeling import models, fitting
from photutils.datasets import make_4gaussians_image
from photutils import centroid_2dg



def photometry(image2d, cen_x, cen_y, index = 0, shape = 'Circ', rad = None, r_in = None, r_out = None, ht = None, wid = None, w_in = None, w_out = None, h_out = None, ang = 0.0):
    """
    PARAMETERS
    ----------
    image2d = 2 dimensional image array. Type = ndarray
    cen_x, cen_y = x & y center position. Type = ndarray/list
    index = if cen_x and cen_Y is a list of more than 1 element, specify the desired index. Type = Integer
    shape = 'Circ':CircularAperture, 'Rect':RectangularAperture, 'CircAnn':CircularAnnulus, 'RectAnn':RectangularAnnulus
    rad, r_in, r_out, ht, wid, w_in, w_out, h_out, ang = Astropy's aperture parameters 
    
    RETURNS
    -------
    flux = flux of the image extracted by the aperture described in the "shape" parameter. Type = Float
    aperture = aperture object created by astropy
    """
    
    mask = np.isnan(image2d) == True
    
    if shape == 'Circ':
        aperture = CircularAperture((cen_x[index], cen_y[index]), r = rad)
    elif shape == 'Rect':
        aperture = RectangularAperture((cen_x[index], cen_y[index]), w = wid, h = ht, theta = ang)
    elif shape == 'CircAnn':
        aperture = CircularAnnulus((cen_x[index], cen_y[index]), r_in = r_in, r_out = r_out)
    elif shape == 'RectAnn':
        aperture = RectangularAnnulus((cen_x[index], cen_y[index]), w_in = w_in, w_out = w_out, h_out = h_out, theta = ang)
            
    phot_table = aperture_photometry(image2d, aperture, mask = mask)
    flux = phot_table[0][0]
    return flux, aperture


def gen_center_g2d(center_x, center_y, box_width, amp, x_std, y_std, Theta, image, model_plotting = False):
    
    """
    PARAMETERS:
        center_x = x coordinate of the circular aperture; Type = float
        center_y = y coordinate of the circular aperture; Type = float
        amp = amplitude of the gaussian.  Find from the projection curve along the center; Type = float
        x_std = Standard deviation of the Gaussian in x before rotating by theta; Type = float
        y_std = Standard deviation of the Gaussian in y before rotating by theta; Type = float
        Theta = Rotation angle in radians. The rotation angle increases counterclockwise; Type = float
    
    RETURNS:
        seperate_centers =  Center of each image; Type = Array [of tuples]
        x_values = x_value of center of each image; Type = Array
        y_values = y_value of center of each image; Type = Array
    """
        
    #Fitting a gaussian model to each image in image2d list and returning center    
    y_pos, x_pos = np.mgrid[:image.shape[0],:image.shape[1]]
    fit_g = fitting.LevMarLSQFitter()
    gauss2D = models.Gaussian2D(amplitude = amp, x_mean = center_x, y_mean = center_y, x_stddev = x_std, y_stddev = y_std, theta = Theta)
    g = fit_g(gauss2D,x_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width],y_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width],image[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width])
    g1 = fit_g(g,x_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width],y_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width],image[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width])
    new_xCen = g1.x_mean[0]
    new_yCen = g1.y_mean[0]
    
    if model_plotting == True:
        
        plt.subplot(131)
        plt.imshow(image[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width])
        plt.title('Data')
        
        plt.subplot(132)
        plt.imshow(g1(x_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width],y_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width]))
        plt.title('Model')
        
        plt.subplot(133)
        plt.imshow(image[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width] - g1(x_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width],y_pos[center_y-box_width:center_y+box_width,center_x-box_width:center_x+box_width]))
        plt.title('Residual')
    
    #Results
    return new_xCen, new_yCen