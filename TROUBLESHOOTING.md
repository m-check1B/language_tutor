# Troubleshooting Guide for Language Tutor Application

## Backend Server Startup Issues

Follow these steps to diagnose and resolve backend server startup issues:

1. Verify Python installation and version:
   - Open a terminal and run: `python3 --version`
   - Ensure Python 3.7 or higher is installed

2. Check backend directory contents and file permissions:
   - Navigate to the backend directory: `cd /home/matej/github/language_tutor/backend`
   - List contents and permissions: `ls -la`
   - Ensure all files are readable and the main application file is executable

3. Confirm uvicorn installation:
   - Run: `pip list | grep uvicorn`
   - If not installed, run: `pip install uvicorn`

4. Run diagnostic script:
   - Execute: `python3 check_backend.py`
   - Review the output for any errors or missing dependencies

5. Manually attempt to start the backend server:
   - Run: `python3 -m uvicorn app.main:app --reload --port 8000`
   - Note any error messages or unexpected behavior

6. Review error messages and logs:
   - Check for any error messages in the terminal output
   - Look for log files in the backend directory
   - Review system logs: `sudo journalctl -u your-backend-service-name.service`

7. Verify environment variables:
   - Check the contents of the .env file in the backend directory
   - Ensure all required variables are set correctly

## Common Issues and Solutions

1. ModuleNotFoundError:
   - Ensure you're in the correct virtual environment
   - Install missing packages: `pip install -r requirements.txt`

2. Permission denied errors:
   - Check file permissions: `ls -la`
   - Adjust if necessary: `chmod +x filename`

3. Port already in use:
   - Find the process using the port: `sudo lsof -i :8000`
   - Kill the process: `sudo kill -9 PID`

4. Database connection issues:
   - Verify database credentials in .env file
   - Ensure the database server is running

5. Import errors:
   - Check your PYTHONPATH: `echo $PYTHONPATH`
   - Add the project root to PYTHONPATH if necessary

If you encounter any issues not covered here, please document the exact error messages and the steps you've taken, then contact the development team for further assistance.
