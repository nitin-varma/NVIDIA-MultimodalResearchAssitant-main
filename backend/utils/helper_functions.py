# utils/helper_functions.py
import os
import shutil
import fitz
import base64
from io import BytesIO
from PIL import Image
import requests
from llama_index.llms.nvidia import NVIDIA

def set_environment_variables():
    """Set necessary environment variables."""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA API Key is not set. Please check your .env file or environment variables.")
    os.environ["NVIDIA_API_KEY"] = api_key

def get_b64_image_from_content(image_content):
    """Convert image content to a base64 encoded string."""
    img = Image.open(BytesIO(image_content))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def is_graph(image_content):
    """Determine if an image is a graph, plot, chart, or table."""
    description = describe_image(image_content)
    return any(keyword in description.lower() for keyword in ["graph", "plot", "chart", "table"])

def describe_image(image_content):
    """Generate a description of an image using NVIDIA API."""
    image_b64 = get_b64_image_from_content(image_content)
    invoke_url = "https://ai.api.nvidia.com/v1/vlm/nvidia/neva-22b"
    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        raise ValueError("NVIDIA API Key is not set. Please set the NVIDIA_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": f'Describe what you see in this image. <img src="data:image/png;base64,{image_b64}" />'
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.20,
        "top_p": 0.70,
        "seed": 0,
        "stream": False
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise ValueError(f"Failed to communicate with NVIDIA API: {response.status_code} - {response.text}")

    response_data = response.json()
    if "choices" not in response_data or not response_data["choices"]:
        raise ValueError("No description generated. 'choices' key missing in API response.")
    
    return response_data["choices"][0]['message']['content']

def clear_cache_directory(cache_dir):
    """Delete all files and folders inside a specified cache directory and recreate necessary subdirectories."""
    if os.path.exists(cache_dir):
        try:
            # Remove all files and folders inside the directory
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            #print(f"Cleared cache directory: {cache_dir}")
        except Exception as e:
            print(f"Error clearing cache directory: {e}")
    else:
        print(f"Cache directory does not exist: {cache_dir}")
    
    # Ensure the main cache directory exists
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create necessary subdirectories
    vectorstore_dir = os.path.join(cache_dir, "vectorstore")
    table_refs_dir = os.path.join(vectorstore_dir, "table_references")
    image_refs_dir = os.path.join(vectorstore_dir, "image_references")
    
    for dir_path in [vectorstore_dir, table_refs_dir, image_refs_dir]:
        os.makedirs(dir_path, exist_ok=True)
        #print(f"Created directory: {dir_path}")

    #print("Cache directories have been set up.")

def process_graph(image_content):
    """Process a graph image and generate a description using NVIDIA API."""
    description = process_graph_deplot(image_content)
    nvidia_llm = NVIDIA(model_name="nvidia/llama-3.1-nemotron-51b-instruct")
    response = nvidia_llm.complete("Your responsibility is to explain charts. You are an expert in describing the responses of linearized tables into plain English text for LLMs to use. Explain the following linearized table: " + description)
    return response.text

def process_graph_deplot(image_content):
    """Process a graph image using NVIDIA's Deplot API to get the underlying data table."""
    invoke_url = "https://ai.api.nvidia.com/v1/vlm/google/deplot"
    image_b64 = get_b64_image_from_content(image_content)
    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        raise ValueError("NVIDIA API Key is not set. Please set the NVIDIA_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": f'Generate the underlying data table of the figure below: <img src="data:image/png;base64,{image_b64}" />'
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.20,
        "top_p": 0.20,
        "stream": False
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise ValueError(f"Failed to communicate with NVIDIA Deplot API: {response.status_code} - {response.text}")

    response_data = response.json()
    if "choices" not in response_data or not response_data["choices"]:
        raise ValueError("No data table generated. 'choices' key missing in API response.")

    return response_data["choices"][0]['message']['content']

def extract_text_around_item(text_blocks, bbox, page_height, threshold_percentage=0.1):
    """Extract text above and below a given bounding box on a page."""
    before_text, after_text = "", ""
    vertical_threshold_distance = page_height * threshold_percentage
    horizontal_threshold_distance = bbox.width * threshold_percentage

    for block in text_blocks:
        block_bbox = fitz.Rect(block[:4])
        vertical_distance = min(abs(block_bbox.y1 - bbox.y0), abs(block_bbox.y0 - bbox.y1))
        horizontal_overlap = max(0, min(block_bbox.x1, bbox.x1) - max(block_bbox.x0, bbox.x0))

        if vertical_distance <= vertical_threshold_distance and horizontal_overlap >= -horizontal_threshold_distance:
            if block_bbox.y1 < bbox.y0 and not before_text:
                before_text = block[4]
            elif block_bbox.y0 > bbox.y1 and not after_text:
                after_text = block[4]
                break

    return before_text, after_text

def process_text_blocks(text_blocks, char_count_threshold=500):
    """Group text blocks based on a character count threshold."""
    current_group = []
    grouped_blocks = []
    current_char_count = 0

    for block in text_blocks:
        if block[-1] == 0:  # Check if the block is of text type
            block_text = block[4]
            block_char_count = len(block_text)

            if current_char_count + block_char_count <= char_count_threshold:
                current_group.append(block)
                current_char_count += block_char_count
            else:
                if current_group:
                    grouped_content = "\n".join([b[4] for b in current_group])
                    grouped_blocks.append((current_group[0], grouped_content))
                current_group = [block]
                current_char_count = block_char_count

    # Append the last group
    if current_group:
        grouped_content = "\n".join([b[4] for b in current_group])
        grouped_blocks.append((current_group[0], grouped_content))

    return grouped_blocks
