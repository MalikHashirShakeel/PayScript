# 🧾 PayScript

**PayScript** is a Django-based application designed to streamline product management for multiple customers and generate clean, PDF-ready invoices for each customer using **WeasyPrint**. It incorporates modern styling with **Tailwind CSS** to offer a responsive and visually pleasing interface.

---

## 🔧 Prerequisites & Dependencies

Before cloning and running the project, make sure your system meets the following requirements:

### ✅ 1. Python (>= 3.8)

Download & Install: [https://www.python.org/downloads/](https://www.python.org/downloads/)

Check version:
```bash
python --version
````

---

### ✅ 2. Node.js & npm (Required for Tailwind CSS)

Download & Install: [https://nodejs.org/](https://nodejs.org/)

Check versions:

```bash
node -v
npm -v
```

---

### ✅ 3. GTK Runtime (Windows - Required for WeasyPrint)

Install from the link below if you're using Windows:

➡️ [GTK3 Runtime for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2023-02-08/gtk3-runtime-3.24.34-2022-01-10-ts-win64.exe)

---

### ✅ 4. WeasyPrint

Install via pip:

```bash
pip install WeasyPrint
```

Docs: [https://weasyprint.readthedocs.io](https://weasyprint.readthedocs.io)

---

### ✅ 5. Django

Install Django via pip:

```bash
pip install django
```

---

## 📁 Project Structure

```
/project-root
│
├── venv/                  # Virtual Environment (DO NOT DELETE)
├── payscript/             # Main Django Project (contains manage.py)
│   └── core/              # Django App
│
├── requirements.txt       # Project dependencies
└── README.md              # This file
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/MalikHashirShakeel/PayScript.git
cd project-root
```

---

### 2️⃣ Create and activate virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

---

### 3️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Install Tailwind CSS dependencies

```bash
cd payscript
npm install
```

> Ensure your `tailwind.config.js` and `input.css`/`output.css` are set up correctly in the static folder.

---

## 🛠️ Run the Project

Open **two terminals** at the **project root level** (where `venv`, `payscript`, and `requirements.txt` exist):

---

### ✅ Terminal 1 – Django Development Server

```bash
# Activate environment
venv\Scripts\activate
cd payscript

# Run the development server
python manage.py runserver
```

---

### ✅ Terminal 2 – Tailwind CSS Watch Mode

```bash
# Activate environment
venv\Scripts\activate
cd payscript

# Start TailwindCSS in watch mode
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch
```

---

## 👤 Create Superuser

To access the Django Admin:

```bash
cd payscript
python manage.py createsuperuser
```

Then visit the admin panel:

➡️ [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 💡 About PayScript

PayScript is built to simplify your workflow of managing product sheets for clients and generating clean, professional invoices — all in one intuitive dashboard.

Whether you're managing five clients or five hundred, **PayScript** gives you the structure and tools to stay efficient and organized.

---

## 💬 Final Words

> "Every invoice tells a story — of effort, of craft, of value delivered. PayScript is not just a billing system — it's your digital handshake, your signature of professionalism."

Crafted with 💙 and clean code to empower your business workflows By Malik Hashir Shakeel.
Happy Building! 🔨🤖🔧

---

Let me know if you'd like me to automatically add badges, GitHub Actions, `.env` templates, or deployment instructions (Heroku, Vercel, Render, etc.) 🚀
