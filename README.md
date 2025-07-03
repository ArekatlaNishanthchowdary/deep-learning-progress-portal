# Deep Learning Progress Portal

Welcome to the **Deep Learning Progress Portal**, a Streamlit-based web application designed to track and manage progress updates for students and admins in a deep learning course. This portal allows students to submit weekly progress updates, while admins can manage users, enable edits, and clear data with granular control.

## Features
- **Student Functionality**: Submit and (when permitted) update weekly progress updates.
- **Admin Functionality**: 
  - Manage user accounts (add new users).
  - Toggle edit permissions for students.
  - Clear data options: specific week for a user, all data for a user, all data for all users, or a specific week for all users.
  - View and edit student updates.
- **User Interface**: Modern, dark-themed UI with interactive elements and responsive design.
- **Database**: SQLite-based storage for users and updates.

## Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- A GitHub account (for deployment)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ArekatlaNishanthchowdary/deep-learning-progress-portal.git
   cd deep-learning-progress-portal
```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Deploying on Streamlit Cloud

1. Push your code to a public GitHub repository.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in.
3. Click 'New app', select your repo, and set the main file as `app.py`.
4. Click 'Deploy'.

**Note:** The SQLite database will reset on every redeploy or sleep. For persistent data, consider using a cloud database.
