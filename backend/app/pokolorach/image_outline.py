import numpy as np
import cv2
from skimage.measure import label, regionprops
import requests
from io import BytesIO
from copy import deepcopy
from PIL import Image
from app.database import save_image, update_image_entry, get_entry

class ImagePreprocessor:
    @staticmethod
    def preprocess_image(image):
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = np.clip(image, 0, 255).astype(np.uint8)
        return image

class ImageOutline:
    def __init__(self, image, line_size=3, blur_value=3, area_threshold_factor=150):
        self.image = image
        self.line_size = line_size
        self.blur_value = blur_value
        self.area_threshold_factor = area_threshold_factor

    def get_most_frequent_vicinity_value(self, mat, x, y, xyrange):
        ymax, xmax = mat.shape
        vicinity_values = mat[max(y - xyrange, 0):min(y + xyrange, ymax),
                              max(x - xyrange, 0):min(x + xyrange, xmax)].flatten()
        counts = np.bincount(vicinity_values)
        return np.argmax(counts)

    def are_neighbors_same(self, mat, x, y):
        width = mat.shape[1]
        height = mat.shape[0]
        val = mat[y, x]
        neighbors = [(x + 1, y), (x, y + 1)]
        
        for xx, yy in neighbors:
            if 0 <= xx < width and 0 <= yy < height:
                if mat[yy, xx] != val:
                    return False
        return True

    def outline(self, mat):
        height, width = mat.shape
        line_mat = np.zeros((height, width), dtype=np.uint8)
        outlined_pixels = set()

        for y in range(height):
            for x in range(width):
                if (x, y) in outlined_pixels:
                    continue
                
                if self.are_neighbors_same(mat, x, y):
                    if (x + 1 < width and mat[y, x] != mat[y, x + 1]) or \
                       (y + 1 < height and mat[y, x] != mat[y + 1, x]):
                        line_mat[y, x] = 162
                        outlined_pixels.add((x, y))
                    else:
                        line_mat[y, x] = 255
                else:
                    line_mat[y, x] = 162

        return line_mat

    def getRegion(self, mat, cov, x, y):
        covered = deepcopy(cov)
        region = {'value': mat[y][x], 'x': [], 'y': []}
        value = mat[y][x]

        queue = [[x, y]]
        while len(queue) > 0:
            coord = queue.pop()
            if not covered[coord[1]][coord[0]] and mat[coord[1]][coord[0]] == value:
                region['x'].append(coord[0])
                region['y'].append(coord[1])
                covered[coord[1]][coord[0]] = True
                if coord[0] > 0:
                    queue.append([coord[0] - 1, coord[1]])
                if coord[0] < len(mat[0]) - 1:
                    queue.append([coord[0] + 1, coord[1]])
                if coord[1] > 0:
                    queue.append([coord[0], coord[1] - 1])
                if coord[1] < len(mat) - 1:
                    queue.append([coord[0], coord[1] + 1])
        return region
    
    def getRegionColor(self, mat, region):
        y_coords = np.array(region['y'])
        x_coords = np.array(region['x'])
        colors = [self.image[y, x] for x, y in zip(x_coords, y_coords)]
        colors = np.array(colors)
        unique_colors, counts = np.unique(colors, axis=0, return_counts=True)
        most_frequent_color = unique_colors[counts.argmax()]
        return tuple(most_frequent_color)

    def coverRegion(self, covered, region):
        for i in range(len(region['x'])):
            covered[region['y'][i]][region['x'][i]] = True

    def sameCount(self, mat, x, y, incX, incY):
        value = mat[y][x]
        count = -1
        while x >= 0 and x < len(mat[0]) and y >= 0 and y < len(mat) and mat[y][x] == value:
            count += 1
            x += incX
            y += incY
        return count

    def getLabelLoc(self, mat, region):
        x_center = np.mean(region['x']).astype(int)
        y_center = np.mean(region['y']).astype(int)
        
        x_min, x_max = np.min(region['x']), np.max(region['x'])
        y_min, y_max = np.min(region['y']), np.max(region['y'])
        
        label_width = 20
        label_height = 20
        
        if (x_center - label_width // 2 >= x_min and x_center + label_width // 2 <= x_max and
            y_center - label_height // 2 >= y_min and y_center + label_height // 2 <= y_max):
            return {'value': region['value'], 'x': x_center, 'y': y_center}
        else:
            return None

    def getBelowValue(self, mat, region):
        y_max = mat.shape[0] - 1
        x = region['x'][0]
        y = min(region['y'][0] + 1, y_max)
        while y < mat.shape[0] and mat[y, x] == region['value']:
            y += 1
        return mat[min(y, y_max), x]

    def removeRegion(self, mat, region):
        newValue = self.getBelowValue(mat, region)
        for x, y in zip(region['x'], region['y']):
            mat[y, x] = newValue

    def getLabelLocs(self, mat, area_threshold):
        height, width = mat.shape
        covered = np.zeros((height, width), dtype=bool)

        label_locs = []
        label_color_mapping = {} 
        new_label = 1

        labeled_mat, num_features = label(mat, return_num=True, connectivity=1)
        regions = regionprops(labeled_mat)

        label_mapping = {}

        for region in regions:
            if region.area > area_threshold:
                y, x = region.coords[0]
                old_label = mat[y, x]
                if old_label not in label_mapping:
                    color = self.getRegionColor(mat, {'x': region.coords[:, 1], 'y': region.coords[:, 0]})
                    label_mapping[old_label] = (new_label, color)
                    label_color_mapping[new_label] = color
                    new_label += 1

                new_region_label, _ = label_mapping[old_label]
                label_locs.append(self.getLabelLoc(mat, {'value': new_region_label, 'x': region.coords[:, 1], 'y': region.coords[:, 0]}))

        for region in regions:
            if region.area > area_threshold:
                old_label = mat[region.coords[0][0], region.coords[0][1]]
                new_region_label, _ = label_mapping[old_label]
                for coord in region.coords:
                    mat[coord[0], coord[1]] = new_region_label
            else:
                self.removeRegion(mat, {'value': mat[region.coords[0][0], region.coords[0][1]], 'x': region.coords[:, 1], 'y': region.coords[:, 0]})

        return label_locs, label_color_mapping

class ImageAnnotator:
    @staticmethod
    def draw_labels(image, label_locs, font_scale_small, font_scale_medium, font_scale_large, thickness):
        height, width = image.shape[:2]
        
        if height < 500 or width < 500:
            font_scale = font_scale_small
        elif height < 1000 or width < 1000:
            font_scale = font_scale_medium
        else:
            font_scale = font_scale_large

        for label_info in label_locs:
            if label_info is not None:
                position = (label_info['x'], label_info['y'])
                cv2.putText(image, str(label_info['value']), position,
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
        
        return image

class ImageEdgeProcessor:
    @staticmethod
    def edge_mask(image, line_size, blur_value):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, line_size, blur_value)
        return edges

    @staticmethod
    def merge_mask(image, mask):
        return cv2.bitwise_and(image, image, mask=mask)

class OutlineCreator:
    def __init__(self, file_name=None, entry_id=None, image=None, line_size=3, blur_value=3, filter_size=4, area_threshold_factor=150,
                 outline_color=(162, 162, 162), font_scale_small=0.2, font_scale_medium=0.3,
                 font_scale_large=0.5, thickness=1, min_size=500, file_options=None):
        self.file_name = file_name
        self.entry_id = entry_id
        self.image = image
        self.line_size = line_size
        self.blur_value = blur_value
        self.filter_size = filter_size
        self.area_threshold_factor = area_threshold_factor
        self.outline_color = outline_color
        self.font_scale_small = font_scale_small
        self.font_scale_medium = font_scale_medium
        self.font_scale_large = font_scale_large
        self.thickness = thickness
        self.min_size = min_size
        self.file_options = file_options

    @staticmethod
    def convert_to_bytes(image_array):
        image = Image.fromarray(image_array)
        with BytesIO() as byte_stream:
            image.save(byte_stream, format='PNG')
            return byte_stream.getvalue()

    def create_outline(self):
            height, width = self.image.shape[:2]

            self.image = ImagePreprocessor.preprocess_image(self.image)

            if height < self.min_size or width < self.min_size:
                raise ValueError(f"Image dimensions must be at least {self.min_size}x{self.min_size} pixels. Current dimensions: {width}x{height}.")

            area_threshold = max(height, width) // self.area_threshold_factor

            mat = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

            image_outline = ImageOutline(self.image, self.line_size, self.blur_value, self.area_threshold_factor)
            label_locs, label_color_mapping = image_outline.getLabelLocs(mat, area_threshold)

            outlined_image = image_outline.outline(mat)

            blank_image = np.ones((height, width, 3), dtype=np.uint8) * 255
            for y in range(height):
                for x in range(width):
                    if outlined_image[y, x] == 162:
                        blank_image[y, x] = self.outline_color

            final_image_with_labels = ImageAnnotator.draw_labels(blank_image, label_locs, self.font_scale_small,
                                                                self.font_scale_medium, self.font_scale_large, self.thickness)
            
            outline_image = OutlineCreator.convert_to_bytes(image_array=final_image_with_labels)
            response, image_url = save_image(storage_path="outline_image", file_contents=outline_image, filename=self.file_name, file_options=self.file_options)
            update_image_entry(table_name="Entries", image_url=image_url, entry_id=self.entry_id, column="img_outline_url")
            img_outline_url = get_entry(table_name="Entries", entry_id=self.entry_id, column="img_outline_url")

            return final_image_with_labels, img_outline_url, label_color_mapping
