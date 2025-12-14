import os
import firebase_admin
from firebase_admin import credentials, storage, firestore
from pathlib import Path
import mimetypes

# Initialize Firebase
try:
    cred = credentials.Certificate('firebase_key.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'padel-shop-a94ae.appspot.com'  # Replace with your actual bucket
    })
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit(1)

db = firestore.client()
bucket = storage.bucket()

# Path to assets folder
assets_folder = 'assets'

print("Starting image upload process...")
print("=" * 60)

# Get all images from assets folder
image_files = [f for f in os.listdir(assets_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
print(f"Found {len(image_files)} images in assets folder\n")

# Upload images to Firebase Storage
uploaded_images = {}

for idx, image_file in enumerate(image_files, 1):
    local_path = os.path.join(assets_folder, image_file)
    
    # Create a clean storage path
    storage_path = f'products/{image_file}'
    
    print(f"[{idx}/{len(image_files)}] Uploading: {image_file}")
    
    try:
        # Upload to Firebase Storage
        blob = bucket.blob(storage_path)
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(local_path)
        if mime_type is None:
            mime_type = 'image/jpeg'
        
        # Upload with public read access
        blob.upload_from_filename(local_path, content_type=mime_type)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Get public URL
        public_url = blob.public_url
        
        # Store mapping of filename to URL
        uploaded_images[image_file.lower()] = public_url
        
        print(f"  ✓ Uploaded successfully")
        print(f"  URL: {public_url}\n")
        
    except Exception as e:
        print(f"  ✗ Error uploading {image_file}: {e}\n")
        continue

print("=" * 60)
print(f"\nSuccessfully uploaded {len(uploaded_images)} images")
print("\nNow updating Firestore product documents...")
print("=" * 60)

# Get all products from Firestore
products_ref = db.collection('products')
products = products_ref.stream()

updated_count = 0
skipped_count = 0

for product_doc in products:
    product_data = product_doc.to_dict()
    product_id = product_doc.id
    product_name = product_data.get('name', '').lower()
    
    # Try to match product with an image based on name similarity
    matched_image_url = None
    
    # Direct filename match
    for image_filename, image_url in uploaded_images.items():
        image_name = os.path.splitext(image_filename)[0].lower()
        
        # Check if image name is in product name or vice versa
        if image_name in product_name or product_name in image_name:
            matched_image_url = image_url
            print(f"✓ Matched: '{product_name}' -> '{image_filename}'")
            break
    
    if matched_image_url:
        # Update the product with the real image URL
        products_ref.document(product_id).update({
            'imageUrl': matched_image_url,
            'imageUrls': [matched_image_url]
        })
        updated_count += 1
    else:
        print(f"⚠ No match found for: '{product_name}'")
        skipped_count += 1

print("\n" + "=" * 60)
print(f"\n✅ Upload Complete!")
print(f"   - {len(uploaded_images)} images uploaded to Firebase Storage")
print(f"   - {updated_count} products updated with image URLs")
print(f"   - {skipped_count} products without matching images")
print("\nAll images are now publicly accessible via Firebase Storage!")
