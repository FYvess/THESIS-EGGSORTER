Egg Sorter Dashboard
Overview
The Egg Sorter Dashboard is a web-based application designed to help users manage and visualize data related to egg sorting processes. This dashboard leverages various JavaScript libraries and frameworks to provide an interactive and user-friendly interface. It's complemented by Raspberry Pi scripts that handle the core machine interactions, including the GUI, camera, and weight sensor architecture on the egg sorter machine itself.

Features
Data Visualization: Utilizes ECharts for creating interactive charts and graphs, providing clear insights into sorting data.

Responsive Design: Ensures compatibility across different devices and screen sizes for flexible access.

Customizable: Offers various configuration options to tailor the dashboard to specific needs and data display preferences.

Machine Control Integration: Features underlying Python scripts for Raspberry Pi to manage the egg sorter's hardware, including:

GUI Control: Scripts for the graphical user interface running on the Raspberry Pi.

Camera Integration: Manages camera operations for visual data capture during sorting.

Weight Sensor Architecture: Interacts with weight sensors to collect and process egg weight data.

Installation
To get started with the Egg Sorter Dashboard, follow these steps:

Clone the repository:

git clone https://github.com/FYvess/THESIS-EGGSORTER.git
cd THESIS-EGGSORTER

Install Python dependencies:

pip install flask
# Add any other Python dependencies here, especially for the Raspberry Pi scripts
# e.g., pip install opencv-python RPi.GPIO smbus etc.

Note: Ensure your Raspberry Pi environment has the necessary libraries for camera, GPIO, and sensor interaction.

Run the web application:

python app.py

(If your main web server script is different, update app.py accordingly.)

Usage
Once the web application is running, you can access the dashboard by navigating to http://localhost:3000 (or the port specified by your Flask app) in your web browser. The dashboard provides various features for managing and visualizing egg sorting data. The Raspberry Pi scripts for machine interaction run separately on the egg sorter hardware.

Project Structure
assets/vendor/echarts/: Contains ECharts files for data visualization.

static/style.css: Contains custom CSS styles for the dashboard.

charts-echarts.html: Example HTML file demonstrating the use of ECharts.

outer/: This directory contains the Raspberry Pi scripts for the GUI, camera, and weight sensor architecture on the egg sorter machine.

outer/CameraEstimation.py

outer/LinearRegression.py

outer/WeightSensor.py

app.py: (Presumed Flask application entry point) Handles backend logic for the web dashboard.

README.md: This project description file.

LICENSE: Contains the licensing information for the project.

Contributing
We welcome contributions to the Egg Sorter Dashboard. If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

License
This project is licensed under the terms of the GNU General Public License Version 2 or later. For full details, please refer to the LICENSE file.
