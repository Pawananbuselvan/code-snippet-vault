# Developer Code Snippet & Algorithm Vault

A full-stack web application built with **Python, Flask, SQLite, HTML/CSS, and JavaScript** to store, organize, search, and copy reusable code templates across C++, Python, C#, SQL, and JavaScript.

## Features
- **Full REST CRUD Operations:** Create (`POST`), read/filter (`GET`), and delete (`DELETE`) code snippets asynchronously using the JavaScript Fetch API.
- **Normalized Relational Database (3NF):** Uses linked `languages` and `snippets` SQLite tables with Primary and Foreign Key constraints.
- **SQL Analytics & Real-Time Search:** Aggregates snippet counts per language via `LEFT JOIN` and `GROUP BY`, and filters snippets in real time via `INNER JOIN` and `LIKE` pattern matching.
- **One-Click Clipboard Copy:** Copies formatted code blocks directly to the clipboard for fast reuse.

## Setup & Local Execution
1. Clone the repository:
   ```bash
   git clone [https://github.com/Pawananbuselvan/code-snippet-vault.git](https://github.com/Pawananbuselvan/code-snippet-vault.git)
   cd code-snippet-vault

installs:
```bash
pip install flask
```
after completion
```
python app.py

```
Open http://127.0.0.1:5000 in your browser.

