# MineFootprint: Carbon Footprint Analyser for Coal Mines

MineFootprint is a web-based platform designed to help coal mining operations track, analyze, and reduce their carbon footprint. It provides detailed, mine-specific carbon emission calculations, visualizations, and actionable insights, with a focus on Indian mining practices.

## Features

- **Comprehensive Data Collection:** Capture all emission sources, including fugitive methane, transportation, and post-mining activities.
- **Mine-Specific Variables:** Account for coal properties, mining depth, ventilation rates, and regional factors.
- **Real-Time Monitoring:** Track emissions continuously, not just annually.
- **Differentiated Analysis:** Separate calculations for open-cast and underground mines.
- **Interactive Visualizations:** Pie charts, trend lines, and benchmarking against industry standards.
- **Project Management:** Save, edit, and compare multiple projects/years.
- **India-Focused Parameters:** Incorporate local coal characteristics and mining practices.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Database:** SQLite (default, can be changed)
- **Authentication:** Django's built-in user system

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/MineFootprint.git
   cd MineFootprint
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the app:**
   Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Usage

- Register or log in to create and manage projects.
- Use the "Calculator" to input mine-specific data and compute your carbon footprint.
- View results with detailed breakdowns and visualizations.
- Save projects for future reference and comparison.

## Project Structure

- `Model/` - Django app for core models, views, templates, and static files.
- `Pages/` - Static pages (home, about us) and related assets.
- `UserAuth/` - User authentication and profile management.
- `Trial/` - Django project settings.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Chart.js](https://www.chartjs.org/)
- [Font Awesome](https://fontawesome.com/)

---
*Empowering coal mines to measure, manage, and mitigate their carbon footprint.*
