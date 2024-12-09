
# [xRI Alpha Sandbox Dataset](https://www.xri.online/)


## Summary
During the winter of 2024, two Built Environment Scanning Systems (BESS) were deployed at scale across eight UK cities. BESS is a platform equipped with optical and infrared cameras, LiDAR as primary sensors, and a suite of additional sensors to derive georeferenced information about the built environment. Each BESS records several terabytes of data weekly.

For this sandbox dataset, raw data has been heavily processed and distilled to make it more usable and to reduce storage requirements. The result is a compact, information-rich geospatial dataset.

## Structure and Datatypes
The dataset is organized using a georeferenced format based on the UK National Unique Property Reference Number (UPRN). Each UPRN is linked to WGS84 latitude, longitude coordinates, and easting and northing in the British National Grid (BNG). Data is stored in directories by UPRN, with subfolders for date, time, and whether it was day or night. An example folder structure is provided below:

We have divided the data into six parts of approximately 10GB each, this is to hopefully increase the ease of downloading this dataset. 
```
data
└── part-1
    └──100100136730
        └── 2024-04-08-18-32-11_day
            ├── centre.pcd.br
            ├── icp_merged.pcd.br
            ├── ir_color_2024-04-08-18-38-01.png
            ├── ir_temp_2024-04-08-18-38-01.npz
            ├── nearir_2024-04-08-18-38-01.png
            ├── range_2024-04-08-18-38-01.png
            ├── reflec_2024-04-08-18-38-01.png
            ├── rgb_2024-04-08-18-38-01.jpeg
            ├── rgb_2024-04-08-18-38-01_anon_masks.json
            ├── sam_mask_rgb_2024-04-08-18-38-01.jpeg
            ├── sam_mask_rgb_2024-04-08-18-38-01.npz
            └── signal_2024-04-08-18-38-01.png
```

### Available Datatypes

#### RGB
- **Description:** Optical color camera images in compressed JPEG format.
- **Files:** 
  - `rgb_<datetime>.jpeg`
  - `rgb_<datetime>_anon_masks.json`
  - `sam_mask_rgb_<datetime>.jpeg`
  - `sam_mask_rgb_<datetime>.npz`
- **Note:** RGB images are excluded for buildings captured at night.

RGB images have been processed so that humans and vehicles have been masked. The anonomising masks themselves are contained in `rgb_<datetime>_anon_masks.json`. The [Mask R-CNN](https://arxiv.org/pdf/1703.06870) with the weights available from [pytorch](https://pytorch.org/vision/stable/models/generated/torchvision.models.detection.maskrcnn_resnet50_fpn.html#maskrcnn-resnet50-fpn) was used to generate these masks.  
The RGB images have also been processed using [Meta's Segment Anything Model (SAM) 2](https://ai.meta.com/sam2/), this model attempts to find all the contiguous objects in an image and produce a mask for them. A visual representation of this is contained in `sam_mask_rgb_<datetime>.jpeg` and the masks themselves are in a compressed numpy array `sam_mask_rgb_<datetime>.npz`.

#### Infrared (IR)
- **Temperature Data:** Radiometric temperature values are stored in a compressed 2D NumPy array (`ir_temp_<datetime>.npz`).
  - Masked pixels should be ignored.
  - Sky pixels are generally invalid for analysis due to differing thermal physics.
- **Colorized Image:** For visualization purposes only (`ir_color_<datetime>.png`).
- **Recommendation:** Use temperature arrays captured at night to avoid solar influence unless analyzing thermal albedo.

#### LiDAR
- **Panoramas:** Four 360-degree greyscale panoramas are provided:
  - `nearir_<datetime>.png`
  - `range_<datetime>.png`
  - `reflec_<datetime>.png`
  - `signal_<datetime>.png`
- **Point Clouds:** Two types of point cloud files:
  - **Orchestrated Point Cloud:** Dense point cloud (`icp_merged.pcd.br`).
  - **Central Point Cloud Frame:** Backup point cloud (`centre.pcd.br`).
- **Compression:** Point clouds are Brotli-compressed for storage efficiency.

### Brotli Decompression
Point clouds can be decompressed using the Brotli CLI or a Python package. Instructions for CLI installation are as follows:

#### Fedora/CentOS/RHEL
```bash
sudo dnf install brotli -y
```

#### Ubuntu/Debian
```bash
sudo apt install brotli -y
```

#### macOS
```bash
brew install brotli
```

#### Windows
Install binaries directly or use Windows Subsystem for Linux (WSL) and follow the Debian instructions.

#### Python Package
```bash
pip install brotli 
```

A decompression script is available in the scripts folder of the xri-alpha-sandbox repository to streamline this process.

## Final Remarks
While folders should generally contain all relevant data, there may be instances where certain sensor modalities are missing due to temporary hardware unavailability.


- **Dataset Size:** Approximately 60GB unzipped; an additional 10GB if all point clouds are decompressed.
- **Community:** Reach out to us and find more information on our [Discourse](https://community.xri.online/). You can also connect with us on [LinkedIn](https://www.linkedin.com/company/xri-online).
- **Support:** For assistance, contact [gary@xri.online](mailto:gary@xri.online) or [nathaniel@xri.online](mailto:nathaniel@xri.online).
