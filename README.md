
# 🧪 Rickipedia: Encyclopedia of Rick &amp; Morty Characters

Rickipedia is a modern, responsive web application built with Streamlit and Python, serving as a comprehensive encyclopedia for the universe of Rick and Morty. It allows users to search, filter, and browse characters, episodes, and locations using data sourced directly from the Rick and Morty API.

---

## ✨ Features

- **Character Directory:** Browse hundreds of characters with filtering options for status (Alive, Dead, Unknown), species, and gender.
- **Search Functionality:** Quickly find characters by name.
- **Character Detail View:** View full biographical details, status, last known location, and a list of all episodes the character has appeared in.
- **Episodes & Locations:** Dedicated pages for browsing all episodes and locations, complete with linked information.
- **Dynamic Styling:** Toggle between Dark Mode (default) and Light Mode for a personalized viewing experience.
- **Responsive Design:** Optimized layout for seamless use on both desktop and mobile devices.

---

## 🛠️ Tech Stack

- **Framework:** Python 3.x, Streamlit
- **API:** The Rick and Morty API (REST)
- **Libraries:** `requests` for fetching data, `streamlit` for the front-end UI.
- **Styling:** Custom CSS injected via Streamlit for aesthetic polish and dark/light mode functionality.

---

## 🚀 Setup and Local Development

Follow these steps to get Rickipedia running on your local machine.

### 1. Prerequisites

You must have Python 3.8+ installed.

### 2. Clone the Repository

```sh
git clone https://github.com/0hhh/Rickipedia
cd Rickipedia
```

### 3. Create a Virtual Environment (Recommended)

```sh
python -m venv venv
# On Linux/macOS
source venv/bin/activate
# On Windows
.\venv\Scripts\activate
```

### 4. Install Dependencies

All necessary packages are listed in `requirements.txt`:

```sh
pip install -r requirements.txt
```

### 5. Run the Application

Execute the `app.py` file using Streamlit:

```sh
streamlit run app.py
```

The application will automatically open in your web browser, typically at [http://localhost:8501](http://localhost:8501).

---

## 📂 File Structure

The project is contained in a single file for deployment simplicity:

```
rickipedia/
├── app.py              # Main Streamlit application containing all logic, UI, and CSS.
└── requirements.txt    # List of required Python dependencies (streamlit, requests).
```

---

.𖥔 ݁ ˖🔫.𖥔.👴🏼🥼.˖.👽.˖🥒.𖥔 📟݁ ˖🪐.𖥔. 🛸.⚛˖.𖥔 ݁ 🌀.˖🦠.˖🥒.𖥔 📟݁ ˖🧑‍🔬.𖥔.🧬.𖥔 ݁ ˖🔫.🌌.˖🥒.𖥔 📟݁ ˖🪐.𖥔. 🛸.˖🔬.𖥔.📟.𖥔🤖. ๋࣭ ⭑⚝🛸๋࣭ ⭑⚝
