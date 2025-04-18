# 🎯 JobRecommendation

Welcome to **JobRecommendation** — a complete web-based platform that intelligently connects job seekers with ideal opportunities and helps companies manage their postings and candidates with ease.

This repository contains the final implementation of a job compatibility and recommendation system built with Flask, HTML/CSS, and SQLite.

---

## 📚 Table of Contents

- [About](#about)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## 📖 About

**JobRecommendation** is a lightweight yet powerful job matching system designed to:

- Assist job seekers in discovering jobs tailored to their skills and interests.
- Empower companies to create, manage, and track job listings efficiently.
- Enable seamless interaction between users and companies via an intuitive web interface.

It leverages a basic job-matching algorithm (skills compatibility) and provides separate dashboards for job seekers and recruiters.

---

## 🌟 Features

- ✅ **User Authentication** – Login and registration system.
- 🎯 **Job Compatibility System** – Find jobs that best match your profile.
- 🧠 **Smart Recommendations** – Personalized job suggestions based on profile data.
- 👤 **User Dashboard** – View saved jobs, update profile, and explore opportunities.
- 🏢 **Company Dashboard** – Post, edit, and manage job listings.
- 📄 **Profile Management** – Dynamic profile creation for both job seekers and recruiters.
- 💡 **Clean UI** – Responsive front-end templates using HTML, CSS, and JavaScript.

---

## 📁 Project Structure

.
├── app.py # Main Flask application
├── database.py # SQLite DB setup and models
├── reset_db.py # DB reset/init script
├── instance/
│ └── careerquest.db # SQLite database file
├── static/
│ ├── script.js # Front-end JavaScript
│ └── styles.css # Custom styling
├── templates/ # HTML templates (Jinja2)
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── dashboard.html
│ ├── all_jobs.html
│ ├── job_compatibility.html
│ ├── job_recommendations.html
│ ├── navbar.html
│ └── profile.html
├── login.html # (Optional) Separate login page
├── profile_page.html # (Optional) Separate profile view
├── registration.html # (Optional) Standalone registration page
├── structure.txt # Basic project notes/structure
├── .gitignore
├── requirements.txt
└── README.md

---

## 🛠️ Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Sushan-Adhikari/JobRecommendation.git
    cd JobRecommendation
    ```

2.  **Create a virtual environment:**

    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Usage

1.  **Initialize/Reset the database:**

    ```bash
    python reset_db.py
    ```

    _Note: This will delete any existing data._

2.  **Run the application:**

    ```bash
    python app.py
    ```

3.  **Visit the app in your browser:**
    Open your web browser and navigate to [`http://127.0.0.1:5001`](http://127.0.0.1:5001)

---

## 🤝 Contributing

Contributions are welcome! To get started:

1.  **Fork** this repository.
2.  **Create your feature branch:**
    ```bash
    git checkout -b feature/YourAmazingFeature
    ```
3.  **Commit your changes:**
    ```bash
    git commit -m 'Add some AmazingFeature'
    ```
4.  **Push to the branch:**
    ```bash
    git push origin feature/YourAmazingFeature
    ```
5.  **Open a Pull Request.** Please provide a clear description of the changes.

---

## 📝 License

This project is licensed under the MIT License — see the `LICENSE` file (if one exists in the repository) for details. If no `LICENSE` file is present, you may want to add one based on the MIT License text.
