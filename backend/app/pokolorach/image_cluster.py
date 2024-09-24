import numpy as np
from PIL import Image, ImageFilter
from sklearn.cluster import KMeans
from skimage import measure, morphology, color
from skimage.color import rgb2lab, lab2rgb
from skimage.restoration import denoise_tv_bregman
from scipy import ndimage
import requests
from io import BytesIO
import os
import cv2
import logging
from collections import deque
from app.database import save_image, update_image_entry, get_entry

class ImageProcessor:
    def __init__(self, image_path=None, image_url=None):
        if image_path:
            self.image = self.load_image(image_path)
        elif image_url:
            self.image = self.load_image_from_url(image_url)
        else:
            raise ValueError("Either image_path or image_url must be provided.")
        
    def load_image(self, image_path):
        image = Image.open(image_path)
        image = image.convert("RGB")
        return image

    def load_image_from_url(self, image_url):
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")
        return image

    def preprocess_image(self, denoise_weight=0.1, blur_radius=4):
        image_array = np.array(self.image)
        denoised_image_array = denoise_tv_bregman(image_array, weight=denoise_weight)
        denoised_image = Image.fromarray((denoised_image_array * 255).astype(np.uint8))
        blurred_image = denoised_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return blurred_image
    
    @staticmethod
    def convert_to_bytes(image_array):
        image = Image.fromarray((image_array * 255).astype(np.uint8) if image_array.max() <= 1 else image_array.astype(np.uint8))
        with BytesIO() as byte_stream:
            image.save(byte_stream, format='PNG')
            return byte_stream.getvalue()

class ColorClusterer:
    def __init__(self, image_array):
        self.image_array = image_array
        self.lab_array = rgb2lab(image_array)
    
    def cluster_image(self, n_clusters=16):
        x = self.lab_array[:, :, 0].flatten()
        y = self.lab_array[:, :, 1].flatten()
        z = self.lab_array[:, :, 2].flatten()
        data = np.vstack((x, y, z)).T
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, init="k-means++")
        kmeans.fit(data)
        
        self.centers = kmeans.cluster_centers_
        self.labels = kmeans.labels_
    
    def map_clusters_to_image(self):
        clustered_image = self.centers[self.labels]
        return clustered_image.reshape(self.image_array.shape[:2] + (3,))

    def process_clusters_to_rgb(self, clustered_image):
        return lab2rgb(clustered_image)

    def apply_morphological_closing(self, clustered_image, kernel_size=(5, 5)):
        kernel = np.ones(kernel_size, np.uint8)
        
        if clustered_image.ndim == 3 and clustered_image.shape[2] == 3:
            closed_image = np.zeros_like(clustered_image)
            for i in range(3):
                closed_image[:, :, i] = morphology.closing(clustered_image[:, :, i], kernel)
        else:
            closed_image = morphology.closing(clustered_image, kernel)
        
        closed_image_flat = closed_image.reshape(-1, 3)
        centers_flat = self.centers.reshape(-1, 3)
        distances = np.linalg.norm(closed_image_flat[:, np.newaxis] - centers_flat, axis=2)
        nearest_centers = np.argmin(distances, axis=1)
        reassigned_image = self.centers[nearest_centers].reshape(closed_image.shape)
        
        return reassigned_image

class FacetProcessor:
    def __init__(self, clustered_image):
        self.clustered_image = clustered_image

    def remove_and_fill_small_facets(self, min_size):
        if self.clustered_image.dtype != np.uint8:
            image = (self.clustered_image * 255).astype(np.uint8)
        else:
            image = self.clustered_image.copy()

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        labeled_image = measure.label(gray_image)
        
        cleaned_labels = morphology.remove_small_objects(labeled_image, min_size=min_size)

        mask = cleaned_labels > 0

        cleaned_image = image.copy()
        cleaned_image[~mask] = 0

        if self.clustered_image.dtype != np.uint8:
            cleaned_image = cleaned_image.astype(self.clustered_image.dtype) / 255.0

        black_pixel_mask = np.all(cleaned_image == [0, 0, 0], axis=-1)
        black_pixel_indices = np.argwhere(black_pixel_mask)

        for y, x in black_pixel_indices:
            if x > 0:
                if np.all(cleaned_image[y, x - 1] == [0, 0, 0]) and y > 0:
                    cleaned_image[y, x] = cleaned_image[y - 1, x]
                else:
                    cleaned_image[y, x] = cleaned_image[y, x - 1]
            else:
                if x < cleaned_image.shape[1] - 1:
                    if np.all(cleaned_image[y, x + 1] == [0, 0, 0]) and y > 0:
                        cleaned_image[y, x] = cleaned_image[y - 1, x]
                    else:
                        cleaned_image[y, x] = cleaned_image[y, x + 1]

        return cleaned_image

class ClusteredImageCreator:
    def __init__(self, image_path=None, image_url=None, n_clusters=16, blur_radius=4, denoise_weight=0.1, min_size=300, file_name=None, entry_id=None, file_options=None):
        self.image_path = image_path
        self.image_url = image_url
        self.n_clusters = n_clusters
        self.blur_radius = blur_radius
        self.denoise_weight = denoise_weight
        self.min_size = min_size
        self.file_name = file_name
        self.entry_id = entry_id
        self.file_options = file_options
        self.clustered_image = None

    def create_cluster(self):
        # Process the image
        image_processor = ImageProcessor(self.image_path, self.image_url)
        processed_image = image_processor.preprocess_image(self.denoise_weight, self.blur_radius)
        processed_image_array = np.array(processed_image)

        # Check image dimensions
        if processed_image_array.shape[0] < self.min_size or processed_image_array.shape[1] < self.min_size:
            raise ValueError(f"Image dimensions must be at least {self.min_size}x{self.min_size} pixels. Current dimensions: {processed_image_array.shape[1]}x{processed_image_array.shape[0]}.")

        # Cluster the image
        color_clusterer = ColorClusterer(processed_image_array)
        color_clusterer.cluster_image(self.n_clusters)

        clustered_lab_image = color_clusterer.map_clusters_to_image()
        closed_clustered_lab_image = color_clusterer.apply_morphological_closing(clustered_lab_image)
        self.clustered_image = color_clusterer.process_clusters_to_rgb(closed_clustered_lab_image)

        facet_processor = FacetProcessor(self.clustered_image)
        self.clustered_image = facet_processor.remove_and_fill_small_facets(self.min_size)

        # Save and update image
        clustered_image_bytes = ImageProcessor.convert_to_bytes(self.clustered_image)
        response, image_url = save_image(storage_path="cluster_image", file_contents=clustered_image_bytes, filename=self.file_name, file_options=self.file_options)
        update_image_entry(table_name="Entries", image_url=image_url, entry_id=self.entry_id, column="img_cluster_url")
        img_cluster_url = get_entry(table_name="Entries", entry_id=self.entry_id, column="img_cluster_url")

        return self.clustered_image, img_cluster_url


