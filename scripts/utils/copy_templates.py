import os
import shutil

src_dir = 'ai_health_application'
dest_dir = 'web_app/templates'
static_dir = 'web_app/static/images'

os.makedirs(dest_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# List of folders in ai_health_application
for item in os.listdir(src_dir):
    item_path = os.path.join(src_dir, item)
    if os.path.isdir(item_path):
        html_file = os.path.join(item_path, 'code.html')
        if os.path.exists(html_file):
            # Clean up the name by removing '_careflow_ai'
            clean_name = item.replace('_careflow_ai', '')
            dest_html = os.path.join(dest_dir, f'{clean_name}.html')
            shutil.copy2(html_file, dest_html)
            print(f'Copied {item}/code.html to {dest_html}')
            
        # Copy image if exists
        img_file = os.path.join(item_path, 'screen.png')
        if os.path.exists(img_file):
            clean_name = item.replace('_careflow_ai', '')
            dest_img = os.path.join(static_dir, f'{clean_name}.png')
            shutil.copy2(img_file, dest_img)

print("All templates copied successfully.")
