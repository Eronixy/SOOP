# SOOP - Focus more, code less.

## Introduction
SOOP is an enhanced version of the Java programming language, designed with a Python-like syntax to improve readability, simplify programming for beginners, and provide a shorter, more concise syntax.

## Technology Stack
SOOP Analyzer is built with:
- Vite + React frontend
- Flask backend

## Features
- Python-like syntax for Java programming
- Improved readability and simplicity
- Vite + React frontend for fast and efficient UI development
- Flask backend for robust and scalable server-side processing

## Repository Structure
- `backend/`: Contains the backend implementation in Python.
- `frontend/`: Contains the frontend implementation using React with Vite.

## Prerequisites
- Python
- Node.js
- npm or yarn

## Installation
### Clone the repository:
```
git clone https://github.com/Eronixy/SOOP.git
cd SOOP
```

### Install backend dependencies:
1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Install frontend dependencies:
```
cd ../frontend
npm install
```

## Usage
### Running the Backend
1. Ensure the virtual environment is activated:
   ```
   cd backend
   venv\Scripts\activate   # On Windows
   source venv/bin/activate # On macOS/Linux
   ```
2. Run the application:
   ```
   python app.py
   ```

### Running the Frontend
```
cd frontend
npm run dev
```

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/)
- [React](https://reactjs.org/)
- [Vite](https://vitejs.dev/)
