import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
try:
    cred = credentials.Certificate('firebase_key.json')
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit(1)

db = firestore.client()

# Path to assets folder
assets_folder = 'assets'

print("Updating Firestore with local asset paths...")
print("=" * 60)

# Get all images from assets folder
image_files = [f for f in os.listdir(assets_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
print(f"Found {len(image_files)} images in assets folder\n")

# Create mapping of image names to asset paths
image_map = {}
for image_file in image_files:
    # Asset path format for Flutter
    asset_path = f'assets/{image_file}'
    image_map[image_file.lower()] = asset_path

# Get all products from Firestore
products_ref = db.collection('products')
products = products_ref.stream()

updated_count = 0
skipped_count = 0

print("Matching products to images...\n")

for product_doc in products:
    product_data = product_doc.to_dict()
    product_id = product_doc.id
    product_name = product_data.get('name', '').lower()
    brand = product_data.get('brand', '').lower()
    category = product_data.get('category', '').lower()
    
    # Try to match product with an image
    matched_asset_path = None
    best_match_score = 0
    best_match_file = None
    
    for image_filename, asset_path in image_map.items():
        image_name = os.path.splitext(image_filename)[0].lower()
        
        # Calculate match score
        score = 0
        
        # Category-specific matching for balls, grips, bags
        if 'ball' in category:
            if brand in image_name and 'ball' in image_name:
                score = 100  # Perfect match
            elif 'ball' in image_name:
                score = 50   # Generic ball match
        elif 'overgrip' in category or 'grip' in category:
            if brand in image_name and ('grip' in image_name or 'overgrip' in image_name):
                score = 100  # Perfect match
            elif 'grip' in image_name or 'overgrip' in image_name:
                score = 50   # Generic grip match
        elif 'bag' in category:
            if brand in image_name and 'bag' in image_name:
                score = 100  # Perfect match
            elif 'bag' in image_name:
                score = 50   # Generic bag match
        else:
            # For rackets and other products, match by product name
            # Direct substring match
            if image_name in product_name or product_name in image_name:
                score = 90
            # Product name words in image name
            else:
                name_words = set(product_name.replace('-', ' ').split())
                image_words = set(image_name.replace('-', ' ').replace('_', ' ').split())
                common_words = name_words & image_words
                if len(common_words) >= 2:
                    score = 70
                elif len(common_words) == 1:
                    score = 30
                # Brand match as fallback
                elif brand in image_name:
                    score = 20
        
        if score > best_match_score:
            best_match_score = score
            matched_asset_path = asset_path
            best_match_file = image_filename
    
    if matched_asset_path and best_match_score > 0:
        # Update the product with the asset path
        products_ref.document(product_id).update({
            'imageUrl': matched_asset_path,
            'imageUrls': [matched_asset_path]
        })
        print(f"✓ {category.upper()}: '{product_name}' -> '{best_match_file}' (score: {best_match_score})")
        updated_count += 1
    else:
        # Use a default placeholder
        default_image = 'assets/ultra padel.jpg'  # Use any image as default
        products_ref.document(product_id).update({
            'imageUrl': default_image,
            'imageUrls': [default_image]
        })
        print(f"⚠ No match for: '{product_name}' - using default image")
        skipped_count += 1

print("\n" + "=" * 60)
print(f"\n✅ Update Complete!")
print(f"   - {updated_count} products matched with images")
print(f"   - {skipped_count} products using default image")
print(f"\n📱 All images will load from local assets folder")
print(f"   (No internet connection needed for images!)")
