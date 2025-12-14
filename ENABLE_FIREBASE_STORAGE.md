# Enable Firebase Storage

Your Firebase Storage bucket needs to be created before uploading images.

## Steps to Enable Firebase Storage:

1. **Go to Firebase Console**: https://console.firebase.google.com
2. **Select your project**: `padel-shop-a94ae`
3. **Click on "Storage"** in the left sidebar (under "Build")
4. **Click "Get Started"**
5. **Choose security rules**:
   - Select "Start in test mode" for now (you can change this later)
   - Click "Next"
6. **Select location**:
   - Choose your region (e.g., `us-central1` or closest to your users)
   - Click "Done"

## After Enabling Storage:

Once Storage is enabled, run the upload script again:

```powershell
.venv\Scripts\python.exe upload_images_to_firebase.py
```

The script will upload all 56 images from the `assets` folder to Firebase Storage and update Firestore with the real image URLs.

## What the Script Does:

1. Uploads each image to `products/[imagename].jpg` in Firebase Storage
2. Makes images publicly accessible
3. Matches images to products by name similarity
4. Updates Firestore `imageUrl` and `imageUrls` fields with real URLs

After running, your app will display real product images instead of placeholders!
