#!/bin/bash
set -e
PEM_FILE="Elsai-Package.pem"
FOLDER_NAME="elsai_retrievers"
PACKAGE_NAME="elsai-retrievers"
INDEX_NAME="elsai-retrievers"
DEVPI_SIMPLE_URL="https://elsai-core-package.optisolbusiness.com/root/elsai-retrievers/+simple/$PACKAGE_NAME/"
EC2_DEST_DIR="/home/ubuntu/packages"

# Set EC2 connection details
EC2_HOST="${EC2_HOST:?EC2_HOST not set}"
EC2_PORT="${EC2_PORT:?EC2_PORT not set}"
EC2_USER="ubuntu"
echo ${EC2_HOST}
echo ${EC2_PORT}

# STEP 1: Fetch and increment version
get_next_version_from_devpi() {
  echo "🌐 Fetching latest version of $PACKAGE_NAME from Devpi..." >&2
  html=$(command -v curl > /dev/null && curl -s "$DEVPI_SIMPLE_URL" || wget -qO- "$DEVPI_SIMPLE_URL")
  echo ${DEVPI_SIMPLE_URL} >&2
  latest_version=$(echo "$html" | \
    grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | \
    sort -V | \
    tail -n 1)
  
  if [[ -z "$latest_version" ]]; then
    echo "⚠️ Failed to fetch latest version from Devpi. Fallbacking to default version."  >&2
    echo "0.1.0"
    return
  fi
  
  IFS='.' read -r major minor patch <<< "$latest_version"
  next_patch=$((patch + 1))
  echo "${major}.${minor}.${next_patch}"
}

# Determine version
VERSION=$(get_next_version_from_devpi)
echo "🆕 Auto-inferred version: $VERSION"

# Write version into version.py
echo "📄 Writing version.py for $VERSION"
mkdir -p package
echo "__version__ = \"${VERSION}\"" > package/version.py

echo "🚀 Starting packaging process for version $VERSION..."

# Step 1: Copy ${FOLDER_NAME} into package folder (clean copy)
echo "📁 Copying ${FOLDER_NAME} into package directory..."
rm -rf package/${FOLDER_NAME}
cp -r ${FOLDER_NAME} package/

cd package

# Step 2: Build Cython extensions in-place
echo "⚙️ Building Cython extensions..."
python setup.py build_ext --inplace

# Step 3: Remove implementation.py files (preserve __init__.py)
echo "🧹 Removing source implementation.py files for obfuscation..."
find ${FOLDER_NAME} -type f -name "implementation.py" -delete

# Step 4: Package the project into sdist and wheel
echo "📦 Creating source and wheel distributions..."
python setup.py sdist bdist_wheel

echo "✅ Packaging complete. Files created in:"
ls -lh dist/

# Step 5: Clean up copied folder
echo "🧽 Cleaning up copied ${FOLDER_NAME} directory..."
rm -rf ${FOLDER_NAME}
rm -f version.py

cd ..

WHL_FILE="package/dist/${FOLDER_NAME}-${VERSION}-py3-none-any.whl"
echo "🚀 Uploading $WHL_FILE to EC2..."

# Fix PEM file permissions
chmod 400 "$PEM_FILE"

# Upload file to EC2
if ! scp -i "$PEM_FILE" -P "$EC2_PORT" -o StrictHostKeyChecking=no "$WHL_FILE" "$EC2_USER@$EC2_HOST:/tmp/"; then
  echo "❌ Failed to upload file to EC2"
  exit 1
fi

# === STEP 5: Execute on EC2 ===
echo "🔧 Executing commands on EC2..."
if ! ssh -i "$PEM_FILE" -p "$EC2_PORT" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" \
  "set -e && \
   echo '📂 Creating directory...' && \
   mkdir -p '$EC2_DEST_DIR/$VERSION/$FOLDER_NAME' && \
   mv '/tmp/${FOLDER_NAME}-${VERSION}-py3-none-any.whl' '$EC2_DEST_DIR/$VERSION/$FOLDER_NAME/' && \
   echo '✅ Package moved.' && \
   echo '🧪 Activating conda and uploading to Devpi...' && \
   eval \"\$(~/miniconda3/bin/conda shell.bash hook)\" && \
   conda activate devpienv && \
   devpi login root --password='' && \
   (devpi use ${INDEX_NAME} || (devpi index -c ${INDEX_NAME} bases=root/pypi && echo '🆕 Created index root/${INDEX_NAME}.')) && \
   devpi upload --from-dir '$EC2_DEST_DIR/$VERSION/$FOLDER_NAME' && \
   echo '✅ Upload to Devpi complete.' && \
   echo "☁️ Uploading .whl to S3..."
   aws s3 cp "$EC2_DEST_DIR/$VERSION/$FOLDER_NAME/${FOLDER_NAME}-${VERSION}-py3-none-any.whl" "s3://elsai-packages/$VERSION/"

   echo '🧹 Deleting package folder...' && \
   rm -rf '$EC2_DEST_DIR/$VERSION/$FOLDER_NAME'"; then
  echo "❌ SSH command execution failed"
  exit 1
fi

# === STEP 6: Local Cleanup ===
echo "🏁 Done. Version $VERSION packaged, uploaded, and published to Devpi!"
exit 0