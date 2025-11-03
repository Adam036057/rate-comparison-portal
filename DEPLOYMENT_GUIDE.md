# 🚀 Streamlit Cloud Deployment Guide

## Step-by-Step Instructions

### **Step 1: Prepare Your Files** ✅
You now have these files ready in the `RateComparisonPortal` folder on your Desktop:
- `streamlit_app.py` - Main application file
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `.gitignore` - Files to exclude from Git
- `dialer_top_counts_updated.xlsx` - Pre-loaded Excel file (optional)

### **Step 2: Create a GitHub Account** (if you don't have one)
1. Go to https://github.com
2. Click "Sign up"
3. Follow the registration process

### **Step 3: Create a New Repository on GitHub**
1. Log in to GitHub
2. Click the "+" icon (top right) → "New repository"
3. Name it: `rate-comparison-portal` (or any name you prefer)
4. Choose: **Private** (if your data is sensitive) or **Public**
5. Don't check any boxes (no README, no .gitignore)
6. Click "Create repository"

### **Step 4: Upload Your Files to GitHub**

**Using GitHub Web Interface (Easiest):**
1. On your new repository page, click "uploading an existing file"
2. Open the folder: `C:\Users\adamj\Desktop\RateComparisonPortal`
3. Drag and drop ALL these files into GitHub:
   - `streamlit_app.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
   - `dialer_top_counts_updated.xlsx` (optional - only if you want pre-loaded file)
4. Scroll down and click "Commit changes"

### **Step 5: Deploy on Streamlit Community Cloud**
1. Go to https://share.streamlit.io
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub
4. Click "New app"
5. Fill in:
   - **Repository**: Select your `rate-comparison-portal` repo
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
6. Click "Deploy!"

### **Step 6: Wait for Deployment** ⏳
- Initial deployment takes 2-5 minutes
- You'll see a URL like: `https://your-app-name.streamlit.app`
- Copy this URL and share with your team!

### **Step 7: Share with Your Company** 🎉
1. Copy your app URL
2. Send it to your colleagues
3. Anyone with the link can access it!

---

## ⚠️ Important Notes

### **About the Pre-loaded Excel File**
- If you want the "Use Pre-loaded Excel" option to work, you MUST upload `dialer_top_counts_updated.xlsx` to GitHub
- The file path has been changed to relative path for cloud deployment
- If you don't include this file, users can still upload files manually

### **Privacy Considerations**
- If your data is sensitive, make your GitHub repo **Private**
- Streamlit Cloud can deploy from private repos
- Only people with the app URL can access it (no authentication by default)

---

## 🔧 Updating Your App

After deployment, any changes you push to GitHub will automatically update your app:

1. Make changes to your local files
2. Upload to GitHub (drag and drop or use git)
3. Streamlit Cloud auto-detects changes and redeploys

---

## 📞 Need Help?

Common issues:
- **App won't start**: Check `requirements.txt` has correct package names
- **Excel file not found**: Make sure `dialer_top_counts_updated.xlsx` is in the root folder
- **Module not found**: Add the missing package to `requirements.txt`

