# Additional Data Information

In this document we look at each data modality and note any additional information that would be useful to users of the xri-alpha-sandbox.

## UPRN Level Information

We should briefly note that the [OS Open UPRN](https://osdatahub.os.uk/downloads/open/OpenUPRN), dataset from which we acquire the building identifiers and their geospatial locations, does possess some oddities and errors. 

UPRNs are often assigned to objects we are not interested in, each parks and playgrounds, old postboxes etc..., bits of waste ground where buildings once stood. At this stage in our pipeline development, without manually checking it is very difficult to know if a UPRN is one of an active UPRN with a building or not. Thus, some none buildings can appear in the dataset.

## RGB

The RGB cameras used fisheye lenses to increase their FOV. We performed fisheye lens correction which required the calculation of a number of parameters. Currently this is only calculated for two out of the four cameras used in the creation of this dataset. We still apply distortion correction using the parameters from the calculated cameras to the uncalculated as the values will be very similar, but this is a known limitation and going forward all cameras will have their own distortion correction procedures.

It should also be noted that generally the edges of even the rectified images possess some rectification artefacts and the aim should be to use predominantly the centre of the image.

At some point for a brief period during alpha data capture in winter 2023-24, the RGB cameras were swapped from left to right without this being recorded. They were then swapped back. Therefore, it is possible that in some UPRNs have RGB images are facing the away from the UPRNs. The raw data was screened before the alpha-sandbox was chosen so this should not be the case but it is a possibility to be aware of as we expand the alpha-sandbox dataset.

<p align="center">
  <img src="images/rgb_2024-03-27-08-54-19.jpeg" alt="rgb image" width="45%">
  <img src="images/sam_mask_rgb_2024-03-27-08-54-19.jpeg" alt="sam rgb image" width="45%">
</p>

## IR

Similarly the IR images have been rectified to correct for distortion for their own optics setups. Similarly rectification parameters were only calculated for two out of four cameras, same as the RGB setup.

Unlike the RGB however the outermost regions of the IR images and temperature arrays have been masked out, this is due to hot edges due to the IR detector heating itself up during operation. In the temperature arrays the masked areas are NaN elements in the numpy array.

<p align="center">
  <img src="images/ir_color_2024-03-05-20-29-54.png  " alt="ir image" width="45%">
</p>

This masking is fixed and is empirically ok, programmatically calculating a method for a reliable "hot edges" mask is outstanding work. Hence it is possible that problematic self-heat from the detector does systematically creep into some temperature arrays.

Additionally when working with the IR data there are some assumptions to note about the way in which radiometic temperature pixels themselves are calculated. 

- The formula requires the distance of each pixel from the detector, currently this is a sensible hard coded value, we are in the process of calculating this distance from the lidar. 
- Building materials tend to be in a narrow range of emissivities $\epsilon\in [0.85,0.93]$, we currently hard code a single sensible value for emissivity but are developing methods for estimating building materials dynamically.
- The formula only governs a certain region of materials in a number of variables. This means that temperature arrays calculated for buildings during the night are valid sources of data for understanding temperature. 
- During the day, we are in a reflectance dominated regime due to the influence of the sun, radiometric temperatures calculated in this regime are not reliable. 
- The sky is an object outside the scope of the radiometric temperature calculation, this is a low reflectance, low emissivity regime that our radiometric temperature calculations cannot really say anything meaningful about.

## LiDAR

We have three 360 degree grey scale panormas these are:

- Near-infrared (NIR) capturing light in the near-infrared spectrum (just beyond visible light). NIR is often used to assess vegetation health, surface properties, and for capturing detailed textures in low-light conditions.

<p align="center">
  <img src="images/nearir_2024-03-25-19-43-47.png  " alt="nearir image" width="90%">
</p>

- The range modality provides the distance from the LiDAR sensor to objects in the environment. Each pixel in this image represents a distance measurement in meters or millimeters, creating a depth map of the scene.

<p align="center">
  <img src="images/range_2024-03-25-19-43-47.png  " alt="nearir image" width="90%">
</p>

- The reflectivity image captures the intensity of the LiDAR signal that bounces back to the sensor. Reflectivity depends on the surface material and angle of incidence, making it useful for distinguishing between materials or identifying road markings, signs, and other objects.#

<p align="center">
  <img src="images/reflec_2024-03-25-19-43-47.png  " alt="nearir image" width="90%">
</p>

- The signal strength or return signal intensity measures the quality of the LiDAR return. Stronger signals usually indicate clearer, more reliable measurements. It can also reflect surface properties and environmental conditions.

<p align="center">
  <img src="images/signal_2024-03-25-19-43-47.png  " alt="nearir image" width="90%">
</p>

We also have two pointclouds one is a single frame that is closest to orthogonal to the UPRN, the other is a dense, orchstrated pointcloud created by merging 10 pointcloud frames on either side of the most orthogonal frame using the [Iterative Closes Point (ICP) registration algorithm](http://ki-www.cvl.iis.u-tokyo.ac.jp/class2013/2013w/paper/correspondingAndRegistration/03_Levoy.pdf). 

These 3D maps can be viewed using a tool like `pcl_viewer` (`brew install pcl`, etc...) we see an example of a pointcloud below:

<p align="center">
  <img src="images/icp_merged.png  " alt="rgb image" width="90%">
</p>