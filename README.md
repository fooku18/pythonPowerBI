# Adobe Analytics Report API via PowerBI Python Script

A problem we currently facing in Power BI is the lack of dynamical updates for Adobe Analytics data. While there exists an Adobe Analytics Report Connector for Power BI it lacks the ability to set a moving time period. This results in a tedious resetting of the date range in the Adobe Analytics Connector which takes a lot of time. This project will speed things up via the ability to load Python scripts in Power BI. Just grab a request json from the Adobe Analytics Workspace and place it as a text file for this scripts. See here how to retrieve a json request body:
https://helpx.adobe.com/analytics/kt/using/build-api2-requests-analysis-workspace-feature-video-use.html

### How to make this work in PowerBI
1. Create a Service Account Integration in Adobe IO. See [here](https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/AuthenticationOverview/ServiceAccountIntegration.md) how to do this.
2. Fill out the config.ini file with all respective keys.
3. In order to execute python scripts in PowerBI, you will need to have a working python3 environment. As this app will need to install custom packages ('auth' and 'report') to pythons site-packages folder and you most probably don't want to pollute your global python environment with these custom packages, create a virtual python environment for the PowerBI scripts. See [here](https://docs.python.org/3/tutorial/venv.html) how to get a virtual environment setup and activated.
4. Activate your newly created python virtual environment and install the source distribution in the 'dist' folder. You can do this as follows:
```bash
pip install {PATH_TO_PACKAGE}
```
5. You will also need to install all required packages from 'requirements.txt'. To do this, change to the repository directory and just type the following into your shell:
```bash
pip install -r requirements.txt
```
6. After the packages are installed in you virtual python environment, reference this environment in PowerBI. In order to do so navigate to 'File -> Options and Settings -> Options -> Python Scripting'. Change the Python Home Directory to your newly created virtual environment.
7. Now you can set up a data source connection via python script. Navigate to 'Get Data' and select 'Python Script'. Paste the code from 'getData.py' into the window and execute the script.
8. You are done. If everything is set up correctly, you now should see a pandas DataFrame in PowerBI.
9. You will notice that you only see data for the last 5 days. This is due the standart settings in 'getData.py'. Change the 'setDateRange' function as explained in the comment block above the function.