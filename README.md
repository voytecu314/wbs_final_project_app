## Setup for contributors
(Prerequisites: git and conda installed)
Run all commands from the root folder (wbs_final_project_app).

1. Clone the repo:
```bash
   git clone git@github.com:voytecu314/wbs_final_project_app.git
   cd wbs_final_project_app
```

2. Create conda environment:
```bash
   conda env create -f environment.yml
   conda activate wbs_final_project_app
```

3. Install pre-commit hooks:
```bash
   pre-commit install
```

4. Create .env file
```bash
   touch .env
```
Refer to .env_example and populate the .env file accordingly.

5. Run the App
```bash
   streamlit run app.py
```

6. If already cloned and pulled with 
```bash
   git pull
```
then before running streamlit app (point 5) 
if the RAG document was changed or exchanged
delete vectore_store folder
```bash
   rm -r rag/vectore_store
```
and then update the environment:
```bash
   conda env update
```

