LIBS="libs"

npm install
rm -rf "$LIBS"
pip install --target "$LIBS" --no-deps --requirement requirements.txt
pip install --no-deps --requirement requirements-dev.txt
