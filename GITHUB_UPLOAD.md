# Private GitHub upload

Team: Muhammad Uzair (PES2UG24CS287) and Mokshithreddy Nallaballe (PES2UG24CS284), Section E.

The local repository has no remote configured. Create an empty **private** repository on GitHub, then run these commands from this directory:

```bash
cd /home/wingsfry/Work/volcano-eruption-ml
git remote add origin https://github.com/<your-username>/<private-repo-name>.git
git branch -M main
git push -u origin main
```

After the push, open **Settings -> Collaborators** and add the faculty member and assigned TA accounts. Do not commit `.venv/`, passwords, or GitHub tokens.

The project can be rerun from a fresh clone with:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/train.py
python src/make_artifacts.py
```
