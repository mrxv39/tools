# chatgpt_router

Windows automation tool that **polls the clipboard** and routes what you copy to the right destination:

- **CMD** → open new CMD window and paste (optionally execute)
- **PowerShell** → open new PowerShell window and paste (optionally execute)
- **File write** → if the first non-empty line is a file path, the rest is written to that file (create/overwrite)

## Safety gate for terminal transcripts

When the clipboard looks like a **copied terminal transcript** (prompt + output), commands are executed **only** if:

- The **first command** is repeated as the **last command** (\"closing\" line)
- The closing line is **not executed** (it's just a marker)

This prevents accidental execution when copying incomplete output.

## Install

```cmd
python -m pip install -r requirements.txt