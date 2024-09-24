from .image_cluster import ClusteredImageCreator
from .image_outline import OutlineCreator

def process_image(
    file_name=None,
    entry_id=None,
    file_options=None,
    image_url=None,
    n_clusters=16,
    blur_radius=4,
    line_size=3,
    blur_value=3,
    filter_size=4,
    area_threshold_factor=200,
    outline_color=(162, 162, 162),
    font_scale_small=0.2,
    font_scale_medium=0.3,
    font_scale_large=0.5,
    thickness=1,
    min_size=300,
    denoise_weight=1
):
    """
    Main function to process an image with clustering and outlining.

    Parameters:
    - file_name (str): Base name of the image file (without extension). Use this if image_url is not provided.
    - image_url (str): URL of the image file. Use this if file_name is not provided.
    - n_clusters (int): Number of clusters for KMeans.
    - blur_radius (float): Radius for Gaussian blur.
    - line_size (int): Size of the edges to be detected.
    - blur_value (int): Blur value for edge detection.
    - filter_size (int): Size of the bilateral filter.
    - area_threshold_factor (int): Factor to determine area threshold for label processing.
    - outline_color (tuple): RGB color for the outline.
    - font_scale_small (float): Font scale for small images.
    - font_scale_medium (float): Font scale for medium-sized images.
    - font_scale_large (float): Font scale for large images.
    - thickness (int): Thickness of the text.
    - min_size (int): Minimum size in pixels for a facet to be retained.
    - denoise_weight (float): Weight for denoising.
    """

    # Create the clustered image
    if image_url:
        creator = ClusteredImageCreator(
            file_name=file_name,
            entry_id=entry_id,
            image_url=image_url,
            n_clusters=n_clusters,
            blur_radius=blur_radius,
            denoise_weight=denoise_weight,
            min_size=min_size
        )
    elif file_name:
        creator = ClusteredImageCreator(
            image_path=f"input/{file_name}.jpg",
            n_clusters=n_clusters,
            blur_radius=blur_radius,
            denoise_weight=denoise_weight,
            min_size=min_size
        )
    else:
        raise ValueError("Either file_name or image_url must be provided.")
    
    clustered_image, img_cluster_url = creator.create_cluster()
    

    # Create the outline image
    outline_creator = OutlineCreator(
        file_name=file_name,
        entry_id=entry_id,
        image=clustered_image,
        line_size=line_size,
        blur_value=blur_value,
        filter_size=filter_size,
        area_threshold_factor=area_threshold_factor,
        outline_color=outline_color,
        font_scale_small=font_scale_small,
        font_scale_medium=font_scale_medium,
        font_scale_large=font_scale_large,
        thickness=thickness,
        min_size=min_size,
        file_options=file_options
    )
    outline_image, img_outline_url, label_color_mapping = outline_creator.create_outline()

    return img_cluster_url, img_outline_url, label_color_mapping
