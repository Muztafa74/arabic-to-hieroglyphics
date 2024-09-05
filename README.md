# arabic-to-hieroglyphics
Here's a summary in English for running the project on your machine for the first time:

### 1. **Set Up the Environment:**

1. **Install Python:**
   Make sure Python is installed on your system. Download it from [Python's official website](https://www.python.org/downloads/) and install it.

2. **Create a Virtual Environment:**
   It's a good practice to use a virtual environment to manage dependencies. Open Command Prompt or Terminal, navigate to your project folder, and create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

### 2. **Install Dependencies:**

1. **Install Python Libraries:**
   Navigate to your project folder and, if there is a `requirements.txt` file, install the libraries using:
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not available, install the libraries manually:
   ```bash
   pip install flask googletrans pillow pytesseract
   ```

### 3. **Set Up Tesseract OCR:**

Ensure that Tesseract OCR is installed on your machine. Download it from [Tesseract's GitHub page](https://github.com/tesseract-ocr/tesseract) and make sure its path is added to your system’s PATH variable.

### 4. **Run the Server:**

Once the environment is set up and dependencies are installed, start the server with:
```bash
python app.py
```

You should see a message indicating that the server is running at `http://127.0.0.1:5000/` or a similar URL.

### 5. **Verify the Application:**

Open your web browser and go to `http://127.0.0.1:5000/`. Check that the application is working as expected by entering Arabic text and testing the functionality.

### Notes:

- **If you encounter errors:**
  Check the messages in the terminal when running `app.py` for details on the issue.

- **Update Translation Libraries:**
  Ensure that the `googletrans` library is working correctly, as updates might affect the API usage.

Feel free to ask if you run into any issues!
