# 🌊 FLOODGATE: DPWH Flood Control Projects Data Analysis and Visualization 
FLOODGATE is an interactive data visualization and analysis app to visualize Department Of Public Works And Highways flood control projects from 2020-2024.\

<img width="2558" height="1399" alt="image" src="https://github.com/user-attachments/assets/e84023c7-bd56-4114-a158-c46fc04e0ba5" />   

## 🗺️ Project Structure

```text
FLOODGATE/
│
├── .devcontainer/       # Development container configuration
├── data/                # Dataset files (raw/processed)
├── styles/              # Custom CSS and styling assets
├── views/               # Streamlit application views/pages
│
├── streamlit-app.py     # Main Streamlit application entry point
├── utils.py             # Helper functions and backend logic
└── requirements.txt     # Python dependencies
```

## 🛠️ Setup Instructions

**1. Clone the Repository**

```bash
git clone https://github.com/JIVERU/FLOODGATE.git
cd FLOODGATE
```

**2. Install Requirements**
Install the necessary dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 📊 Dataset

DPWH Flood Control Projects by **BwandoWando**:\
https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects

## 🚀 Usage
Once your environment is configured and datasets are loaded into the data/ directory, launch the interactive dashboard:

```bash
streamlit run streamlit-app.py
```
The application will automatically open in your default web browser at `http://localhost:8501`

## 🧭 Maintenance & Development Notes
 - **Jupyter Notebooks**: Experimental data analysis and visualization drafting can be done via notebooks before porting the final logic into utils.py and views/.
 - **Updating Dependencies:** If you install new packages (e.g., pip install pandas), capture them immediately:
