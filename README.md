# 

Welcome to the **JobRecommendation** project! This repository contains the final implementation of the JobRecommendation application.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## About

JobRecommendation is a job recommendation and management platform. It is designed to help users find job opportunities that match their skills and preferences while enabling companies to manage job postings and applications efficiently.

## Features

- Job compatibility and recommendation system.
- User and company dashboards for managing profiles and job postings.
- Interactive UI with templates for job management and user interaction.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/sushan-adhikari/JobRecommendation.git
    ```
2. Navigate to the project directory:
    ```bash
    cd JobRecommendation
    ```
3. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Initialize the database:
    ```bash
    python reset_db.py
    ```
2. Run the application:
    ```bash
    python app.py
    ```
3. Access the application at:
    ```
    http://127.0.0.1:5001
    ```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add feature-name"
    ```
4. Push to the branch:
    ```bash
    git push origin feature-name
    ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---