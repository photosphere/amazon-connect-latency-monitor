# amazon-connect-latency-monitor

### Installation

Clone the repo

```bash
git clone https://github.com/photosphere/amazon-connect-latency-monitor.git
```

cd into the project root folder

```bash
cd amazon-connect-latency-monitor
```

#### Create virtual environment

##### via python

Then you should create a virtual environment named .venv

```bash
python -m venv .venv
```

and activate the environment.

On Linux, or OsX 

```bash
source .venv/bin/activate
```
On Windows

```bash
source.bat
```

Then you should install the local requirements

```bash
pip install -r requirements.txt

# Node.js和Playwright
npm install playwright
npx playwright install chromium
```
### Build and run the Application Locally

```bash
streamlit run latency_monitor.py
```
### Or Build and run the Application on Cloud9

```bash
streamlit run latency_monitor.py --server.port 8080 --server.address=0.0.0.0 
```

<img width="780" height="722" alt="Image" src="https://github.com/user-attachments/assets/2e808510-39e7-4394-ad27-1e7f4350e689" />
