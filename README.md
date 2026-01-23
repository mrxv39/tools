chatgpt_router

chatgpt_router is a Windows automation tool that visually detects when code is copied from a browser and automatically routes the clipboard content to the correct destination:

Sublime Text → source code

CMD → command-line commands

PowerShell → PowerShell commands

The goal is to make copying from ChatGPT (or similar tools) a one-click, zero-thinking workflow.

Key Features
🔍 Visual Detection

Detects the browser “Copy code” → “Copied” flow using on-screen image matching.

Works near the mouse click position to avoid false positives.

Uses multiscale OpenCV template matching for robustness.

🧭 Smart Routing

Clipboard content is automatically classified and routed:

✍️ Sublime Text

Strict rule: the first line must be a file path.

If no path is present:

❌ Nothing is pasted

⚠️ A Windows alert explains the problem

If the file does not exist:

Required folders are created

The file is created before opening

Sublime is:

Activated if already running

Launched if not running

Content is pasted without the path

The file is automatically saved (Ctrl+S) after paste

🖥️ CMD / PowerShell

Always opens a new terminal window

Pastes the content

Optional automatic execution (Enter)

After execution:

The full terminal output is copied back to the clipboard

⏱️ Reliable Terminal Synchronization

No fixed sleep() guessing

A sentinel token is appended to the command

The system waits until the sentinel appears in terminal output

Ensures commands have fully finished before copying results

Configuration Highlights

Key options in config.py:

press_enter_in_terminal
Execute pasted commands automatically

copy_terminal_text_to_clipboard
Copy full terminal output after execution

terminal_done_timeout_s
Max time to wait for terminal completion

terminal_done_poll_s
How often terminal output is checked

half_box_px
Size of the visual search region near the click

Testing

The project follows strict TDD.

Automated Tests

Located in tests/test_routing_destinations.py

All external effects are mocked:

Clipboard

Windows

Subprocesses

Covers:

Sublime with valid path

Sublime without path (blocked)

File auto-creation

CMD routing

PowerShell routing

Terminal output capture

Run tests:

python -m pytest -q

Typical Workflow

Click Copy code in the browser

The router detects the visual confirmation

Clipboard content is classified

Content is routed automatically:

Code → Sublime

Commands → CMD / PowerShell

Output (if any) ends up back in your clipboard

Project Philosophy

Visual truth over DOM hacks

Zero accidental pastes

Strict rules for editors, flexible rules for terminals

No background magic without tests

Everything observable is tested

Platform

Windows only

Python 3.11+

Requires:

pyautogui

opencv-python

numpy

pyperclip

pytest