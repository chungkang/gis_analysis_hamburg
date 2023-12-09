import numpy as np
from osgeo import gdal, osr
import os

def read_xyz_file(file_path):
    """Read XYZ format file and return NumPy array."""
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1], data[:, 2]

def merge_xyz_to_tif(input_folder, output_tif):
    # 입력 폴더에서 XYZ 파일 목록을 가져옴
    xyz_files = [f for f in os.listdir(input_folder) if f.endswith('.xyz')]

    if not xyz_files:
        print("No XYZ files found in the input folder.")
        return

    # 첫 번째 XYZ 파일을 기반으로 헤더를 가져옴
    x, y, z = read_xyz_file(os.path.join(input_folder, xyz_files[0]))
    rows, cols = len(np.unique(y)), len(np.unique(x))

    # Create a 2D array to store the merged DEM
    merged_dem = np.zeros((rows, cols), dtype=np.float32)

    for xyz_file in xyz_files:
        x, y, z = read_xyz_file(os.path.join(input_folder, xyz_file))
        # Calculate row and column indices
        row_idx = np.searchsorted(np.unique(y), y)
        col_idx = np.searchsorted(np.unique(x), x)

        # Update the merged DEM array
        merged_dem[row_idx, col_idx] = z

    # Get the geotransform from the first XYZ file
    geotransform = (x.min(), np.unique(x)[1] - x.min(), 0, y.max(), 0, -(np.unique(y)[1] - y.min()))

    # Create a new TIF file
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(output_tif, cols, rows, 1, gdal.GDT_Float32)

    # Set geotransform and projection
    dataset.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # Assuming WGS84
    dataset.SetProjection(srs.ExportToWkt())

    # Write the merged DEM to the TIF file
    dataset.GetRasterBand(1).WriteArray(merged_dem)

    # Close the dataset
    dataset = None

    print(f"DEM files merged successfully. Output file: {output_tif}")

if __name__ == "__main__":
    # 입력 폴더와 출력 파일 경로 설정
    input_folder = "C:\\Users\\ck\\workspace\\GIS\\hamburg_gis\\vector\\DGM10_2x2KM_XYZ\\"
    output_file = "C:\\Users\\ck\\workspace\GIS\\hamburg_gis\\rasterdem.tif"

    # XYZ 파일들을 합치는 함수 호출
    merge_xyz_to_tif(input_folder, output_file)

