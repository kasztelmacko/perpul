import numpy as np
from PIL import Image, ImageFilter
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, lab2rgb
from skimage.restoration import denoise_tv_bregman
import requests
from io import BytesIO
import os
import cv2
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
    
    def closing_morphology(self, clustered_image, kernel_size=(5, 5)):
        kernel = np.ones(kernel_size, np.uint8)
        closed_image = cv2.morphologyEx(clustered_image, cv2.MORPH_CLOSE, kernel)
        return closed_image

class FacetProcessor:
    def __init__(self, clustered_image, labels):
        self.clustered_image = clustered_image
        self.labels = labels

    def remove_and_fill_small_facets(self, min_size=100):
        unique_labels, counts = np.unique(self.labels, return_counts=True)
        large_clusters = unique_labels[counts >= min_size]
        mask = np.isin(self.labels, large_clusters).reshape(self.clustered_image.shape[:2])
        filtered_image = np.zeros_like(self.clustered_image)
        filtered_image[mask] = self.clustered_image[mask]

        small_cluster_indices = np.where(~mask)
        for y, x in zip(*small_cluster_indices):
            nearest_large_cluster_pixel = self.find_nearest_large_cluster_pixel(mask, y, x)
            filtered_image[y, x] = nearest_large_cluster_pixel

        return filtered_image

    def find_nearest_large_cluster_pixel(self, mask, y, x):
        height, width = mask.shape
        min_dist = float('inf')
        nearest_pixel = self.clustered_image[y, x]

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and mask[ny, nx]:
                    dist = abs(dy) + abs(dx)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_pixel = self.clustered_image[ny, nx]

        return nearest_pixel

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
        self.clustered_image = color_clusterer.process_clusters_to_rgb(clustered_lab_image)
        self.clustered_image - color_clusterer.closing_morphology(self.clustered_image)

        # Process facets
        facet_processor = FacetProcessor(self.clustered_image, color_clusterer.labels)
        self.clustered_image = facet_processor.remove_and_fill_small_facets(self.min_size)

        # Save and update image
        clustered_image_bytes = ImageProcessor.convert_to_bytes(self.clustered_image)
        response, image_url = save_image(storage_path="cluster_image", file_contents=clustered_image_bytes, filename=self.file_name, file_options=self.file_options)
        update_image_entry(table_name="Entries", image_url=image_url, entry_id=self.entry_id, column="img_cluster_url")
        img_cluster_url = get_entry(table_name="Entries", entry_id=self.entry_id, column="img_cluster_url")

        return self.clustered_image, img_cluster_url


