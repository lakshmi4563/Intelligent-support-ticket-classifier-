# IntelliSupport - Support Ticket Classifier

This is a small web app that sorts customer support tickets automatically. A customer types their problem into a form, a machine learning model decides whether it is a **Technical**, **Billing** or **General Inquiry** ticket, and the ticket shows up on a dashboard for support agents.

Demo video: https://drive.google.com/file/d/1XZv--UiCc8wRhQX_Av5QJSjee5zMVHpV/view?usp=sharing

## How it works

1. The customer fills in a subject and description on the Customer Portal (Streamlit).
2. The portal sends it to a Flask API.
3. The API predicts the category using a TF-IDF + Linear SVM model.
4. The ticket and its category are saved in MongoDB Atlas.
5. Agents open the Agent Dashboard to see all tickets with their category and time.

## Running it locally

You need Python 3.11 or newer, Git, and a free MongoDB Atlas account.

**1. Clone the repo**

```bash
git clone https://github.com/lakshmi4563/intelligent-support-ticket-classifier.git
cd intelligent-support-ticket-classifier
```

Run all the commands below from this folder (the one that has `backend`, `frontend` and `requirements.txt` in it).

**2. Install dependencies**

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS or Linux, use `source venv/bin/activate` instead of the second line.

**3. Set up MongoDB**

In Atlas, create a free cluster, add a database user, and allow your IP address under Network Access. Then copy the connection string.

Copy `.env.example` to `.env` and put your connection string in it:

```
MONGO_URI=your_connection_string_here
```

The `.env` file is ignored by git, so your password is not uploaded.

**4. Start the backend**

```bash
python -m backend.app
```

It runs on http://127.0.0.1:5000. Keep this terminal open.

**5. Start the frontend**

Open a second terminal in the same folder, activate the virtual environment again, and run:

```bash
streamlit run frontend/app.py
```

Open the link Streamlit shows (usually http://localhost:8501). Start the backend before the frontend, otherwise the portal can't connect.

The trained model is already included in the repo (it is under 0.5 MB), so you don't need to train anything to run the app.

## Trying it out

Pick "Customer Portal", submit a ticket, then switch to "Agent Dashboard" and click Refresh Tickets. Some tickets you can try:

- Subject: `Login error` / Description: `I cannot log in to my account. It shows an authentication error after I enter my password.` (Technical)
- Subject: `Charged twice` / Description: `I was charged twice for order 48213. Please refund the duplicate payment.` (Billing)
- Subject: `Return policy` / Description: `What is your return policy for opened items? Can I return something after 30 days?` (General Inquiry)

Tickets are stored in MongoDB, so they are still there after you restart the servers.

## Design and tech choices

The project is split into a frontend, a backend and a database, and the backend code is split into three small files: `app.py` (routes), `classifier.py` (the model) and `database.py` (MongoDB).

- **Python** for everything, so the model, API and UI all live in one language.
- **Streamlit** for the two screens. It let me build the portal and dashboard quickly and spend the time on the actual workflow.
- **Flask** for the API. It is small and easy to connect to the model and the database.
- **scikit-learn (TF-IDF + Linear SVM)** for classification. The tickets are short text with only three categories, so this is fast, needs no GPU and keeps the repo small. A large deep learning model would have been overkill here.
- **MongoDB Atlas** for storage, because it is hosted online, so tickets are not lost when the app restarts and nothing has to be installed locally.

The vectorizer and the SVM are saved together as one scikit-learn pipeline, so the API just passes the raw ticket text to the model.

## The model

No dataset was provided, so I used a public customer support ticket dataset (`data/dataset-tickets-multi-lang3-4k.csv`) and changed it to fit this task. I kept only the English tickets, joined the subject and body into one text, removed duplicates, and grouped the original queues into three categories:

- Technical: Technical Support, IT Support, Service Outages and Maintenance
- Billing: Billing and Payments
- General Inquiry: Customer Service, Product Support, General Inquiry, Returns and Exchanges, Sales and Pre-Sales

Customer Service and Product Support overlapped a lot and were hard to tell apart, so I merged them into General Inquiry. That left 1,376 tickets (Technical 686, General Inquiry 570, Billing 120).

To retrain the model, run `python data/train_model.py`. On a held-out 20% test set it gets about 71% accuracy and a macro F1 of 0.75 (0.78 with 5-fold cross-validation). Billing is the strongest category (F1 0.85).

Limitations:

- Most mistakes are between Technical and General Inquiry. The labels come from the original support queues, not from reading each ticket, so some are unclear.
- The dataset is mostly IT support, not e-commerce. It works well on wording like "authentication error" or "server outage", but a casual message like "the site takes over a minute to load" was labelled General Inquiry.
- Very short or vague tickets can go either way.

With real tickets from the platform, this would improve.

## API

- `POST /api/tickets` takes `{"subject": "...", "body": "..."}`, predicts the category, saves the ticket and returns it. It returns 400 if both fields are empty and 503 if the database can't be reached.
- `GET /api/tickets` returns all saved tickets, newest first.

## Tests

```bash
pytest
```

The tests use the real model but fake the database, so they run without MongoDB or internet.

## Common problems

- **`No module named 'backend'`**: you are in the wrong folder. Go into the folder that contains `backend` and run the command again.
- **"Could not connect to the Flask backend"**: the backend isn't running. Start it first.
- **Submitting a ticket gives status 503**: the app can't reach MongoDB. Check that `.env` exists and that your IP is allowed in Atlas.
- **Warning about a scikit-learn version**: run `python -m pip install -r requirements.txt` to get the pinned versions.

The Flask auto-reloader is turned off on purpose. When it is on, it can keep restarting the server if another program like Streamlit changes files in the Python folder.

## Folder structure

```
backend/     Flask API, classifier, database code, saved model
frontend/    Streamlit app
data/        dataset and train_model.py
scripts/     MongoDB connection check
tests/       pytest tests
```