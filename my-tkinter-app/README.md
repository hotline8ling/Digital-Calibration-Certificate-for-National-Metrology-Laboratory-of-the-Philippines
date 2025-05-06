# My Tkinter Application

This is a simple Tkinter application designed for creating and managing digital calibration certificates. The application allows users to import calibration certificate images and PDFs, process them, and generate XML files.

## Project Structure

```
my-tkinter-app
├── index.py              # Main application script
├── static_info.json      # Configuration data
├── requirements.txt      # Required Python packages
├── pyinstaller.spec      # PyInstaller configuration for creating executable
└── README.md             # Project documentation
```

## Requirements

To run this application, you need to have Python installed along with the required packages. You can install the necessary packages using the following command:

```
pip install -r requirements.txt
```

## Running the Application

To run the application, execute the following command in your terminal:

```
python index.py
```

## Creating an Executable

To create an executable file for the application, you can use PyInstaller. First, ensure you have PyInstaller installed:

```
pip install pyinstaller
```

Then, run the following command in the terminal:

```
pyinstaller pyinstaller.spec
```

This will generate a `dist` folder containing the executable file for your application.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.