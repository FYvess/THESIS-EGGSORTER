# Egg Sorter Dashboard
Proponents: 
Heherson M. Aledia
Franco Yves P. De Santos
Earlvin N. Eustacio
Christine Joyce E. Nacionales
Pauline Shane M. Querido 

## Overview
The Egg Sorter Dashboard is a web-based application designed to help users manage and visualize data related to egg sorting processes. This dashboard leverages modern JavaScript libraries and frameworks to provide an interactive and user-friendly interface. It is complemented by Raspberry Pi scripts that handle the core machine interactions, including the GUI, camera, and weight sensor architecture on the egg sorter machine itself.

## Features
- **Data Visualization:** Utilizes ECharts and other charting libraries for creating interactive charts and graphs, providing clear insights into sorting data.
- **Responsive Design:** Ensures compatibility across different devices and screen sizes for flexible access.
- **Customizable:** Offers various configuration options to tailor the dashboard to specific needs and data display preferences.
- **Machine Control Integration:** Features underlying Python scripts for Raspberry Pi to manage the egg sorter's hardware, including:
  - **GUI Control:** Scripts for the graphical user interface running on the Raspberry Pi.
  - **Camera Integration:** Manages camera operations for visual data capture during sorting.
  - **Weight Sensor Architecture:** Interacts with weight sensors to collect and process egg weight data.

## Installation
To get started with the Egg Sorter Dashboard, follow these steps:

1. **Clone the repository:**

```bash
git clone https://github.com/FYvess/THESIS-EGGSORTER.git
cd THESIS-EGGSORTER
```

2. **Install Python dependencies:**

```bash
pip install flask
# Add any other Python dependencies here, especially for the Raspberry Pi scripts
# e.g., pip install opencv-python RPi.GPIO smbus picamera2 pillow numpy
```

**Note:** Ensure your Raspberry Pi environment has the necessary libraries for camera, GPIO, and sensor interaction. You may also need to install system-level packages for camera and GPIO support.

3. **Run the web application:**

```bash
cd egg-sorter-dashboard-main
python app.py
```

(If your main web server script is different, update `app.py` accordingly.)

## Usage
Once the web application is running, you can access the dashboard by navigating to `http://localhost:5000` (or the port specified by your Flask app) in your web browser. The dashboard provides various features for managing and visualizing egg sorting data. The Raspberry Pi scripts for machine interaction run separately on the egg sorter hardware.

## Project Structure
```
THESIS-EGGSORTER/
├── CameraEstimation.py           # Raspberry Pi script for camera and GUI
├── LinearRegression.py           # Raspberry Pi script for regression/weight estimation
├── WeightSensor.py               # Raspberry Pi script for weight sensor interaction
├── egg-sorter-dashboard-main/    # Web dashboard application
│   ├── app.py                    # Flask application entry point
│   ├── db.py                     # Database logic for Flask app
│   ├── app.db                    # SQLite database for dashboard
│   ├── schema.sql                # Database schema
│   ├── static/                   # Static files (CSS, JS, images)
│   ├── templates/                # HTML templates for Flask
│   ├── NiceAdmin/                # Admin dashboard UI (HTML, CSS, JS)
│   └── ...
├── README.md                     # This project description file
├── LICENSE                       # Project license
```

### Notable Files and Directories
- `assets/vendor/echarts/`: Contains ECharts files for data visualization.
- `static/style.css`: Contains custom CSS styles for the dashboard.
- `charts-echarts.html`: Example HTML file demonstrating the use of ECharts.
- `CameraEstimation.py`, `LinearRegression.py`, `WeightSensor.py`: Raspberry Pi scripts for the GUI, camera, and weight sensor architecture on the egg sorter machine.
- `app.py`: Flask application entry point for the web dashboard.

## Contributing
We welcome contributions to the Egg Sorter Dashboard. If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License
This project is licensed under the terms of the GNU General Public License Version 2 or later. For full details, please refer to the LICENSE file.
