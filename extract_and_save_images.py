import json
import base64
import os
import argparse
import streamlit as st
from zipfile import ZipFile

def extract_and_save_images(notebook_path, output_dir, output_notebook_path):
    try:
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
        
        os.makedirs(output_dir, exist_ok=True)

        total_image_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            attachments = cell.get('attachments', {})
            new_source_lines = []

            for attachment_name, attachment_data in attachments.items():
                for image_format, image_base64 in attachment_data.items():
                    image_bytes = base64.b64decode(image_base64)
                    image_extension = image_format.split('/')[-1]
                    image_filename = f"cell_{cell_num}_image_{total_image_count}.{image_extension}"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                    new_source_lines.append(f"![Image]({image_path})\n")
                    
                    total_image_count += 1

            if total_image_count > 0:
                cell['attachments'] = {}
                cell['source'] = new_source_lines

        with open(output_notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)

        # Create a zip file with the images folder
        with ZipFile( output_dir+'.zip' , 'w') as zipf:
            zipf.write(output_notebook_path)
            for root, _, files in os.walk(output_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

        st.success(f"Extracted {total_image_count} images to {output_dir} and updated the notebook. Saved as {output_notebook_path}")
        st.markdown(f"### [Download Output Zip File](./{output_dir+'.zip'})")

    except FileNotFoundError:
        st.error(f"File not found: {notebook_path}")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from the file: {notebook_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract images from a Jupyter notebook and save them to a directory")
    parser.add_argument("notebook_path", type=str, help="Path to the Jupyter notebook file")
    parser.add_argument("output_dir", type=str, help="Directory to save the extracted images", default="extracted_images")
    parser.add_argument("output_notebook_path", type=str, help="Path to save the updated notebook with image paths", default="updated_notebook.ipynb")
    args = parser.parse_args()

    extract_and_save_images(args.notebook_path, args.output_dir, args.output_notebook_path)

if __name__ == "__main__":
    main()
        

