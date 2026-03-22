# Implementation Plan: RecycleX Platform

## Goal Description
Build a comprehensive MVP platform for RecycleX with two distinct panels: Users (Sellers) and Admins (Buyers). The system demands a long registration form with OTP verification, a business profile for admins, and a dashboard for both roles. Furthermore, cutting-edge python functionalities tailored for hackathons correspond to AI waste classification (OpenCV/TensorFlow), Smart route optimization (scikit-learn), and an Impact Predictor (pandas). The platform should feature an extremely attractive, modern UI.

## User Review Required
> [!IMPORTANT]
> The backend relies on OpenCV, TensorFlow, Scikit-Learn, and Pandas. Installing these will make the environment heavier but complies directly with your instructions.
> For the "OTP verification", since we do not have a live SMS/email API key (like Twilio or SendGrid) specified, I plan to simulate the OTP by logging it to the backend console and requiring the user to type it in the frontend. Is this acceptable for your hackathon demo?
> For the AI classification, we will use a pre-trained MobileNetV2 model (or a lightweight equivalent) via TensorFlow/Keras to classify uploaded scrap images into generic waste categories.
>
> **Please approve this approach or let me know if you would prefer different tools.**

## Proposed Changes

### Backend Infrastructure
- Fix up [backend/main.py](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/backend/main.py). Currently, there are two `app = FastAPI()` initializations in the same file causing conflicts.
- Consolidate all endpoints (register, login, book_pickup, upload_scrap).
- Create robust SQLite tables:
  - `users`: id, name, email, password, phone, address, city, state, pincode, role (user/admin), eco_points, co2_saved.
  - [pickups](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/backend/main.py#100-108): id, user_id, scrap_type, address, status, lat, lon (for routing).
  - [scrap](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/backend/main.py#166-184): id, seller_id, image, type, price, status.
- Add OTP generation endpoints `/generate_otp` and `/verify_otp`.

#### [MODIFY] [backend/main.py](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/backend/main.py)
Rewrite to consolidate all routes. Include OTP mock flow. Include Gamified rewards logic upon pickup completion.

#### [MODIFY] [backend/requirements.txt](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/backend/requirements.txt)
Add `tensorflow`, `opencv-python-headless`, `scikit-learn`, `pandas`.

#### [MODIFY] [backend/ai_model.py](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/backend/ai_model.py)
Implement real image classification using TensorFlow/Keras and OpenCV rather than the current `random.choice()` mock.

#### [NEW] `backend/route_optimizer.py`
Use `scikit-learn` to cluster or order pickup coordinates logically, matching collectors to nearest points.

#### [NEW] `backend/impact_predictor.py`
Use `pandas` to aggregate data and compute CO2 savings/recycling percentages.

---

### Frontend & UI Design
- Discard the current barebones HTML and completely rewrite the frontend using vanilla HTML/JS but with extremely attractive, custom CSS (glassmorphism, vibrant gradients, animations, modern typography like 'Inter').
- **Pages to Build/Update**:
  - [index.html](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/frontend/index.html): Stunning landing page highlighting features.
  - [register.html](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/frontend/register.html): Long registration form with dropdown for role (User/Seller vs Admin/Buyer) and OTP verification step.
  - [login.html](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/frontend/login.html): Login form with OTP layer.
  - `dashboard_user.html`: User profile dashboard with navigation bar inside profile. Shows Green Points, CO2 saved, and Scrap AI upload tool.
  - `dashboard_admin.html`: Business profile for admins. Shows the Marketplace of available scrap and Smart Route Optimizer for pickups.

#### [MODIFY] [css/style.css](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/css/style.css)
Inject premium, modern dark-mode aesthetics with neon accents, hover effects, and responsive layout.

#### [MODIFY] [frontend/register.html](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/frontend/register.html) & [frontend/login.html](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/frontend/login.html)
Embed the new aesthetic and connect OTP fetch logic in [js/app.js](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/js/app.js).

#### [NEW] `frontend/dashboard_user.html`
Premium user panel displaying the Gamified Rewards and Impact Predictor metrics.

#### [NEW] `frontend/dashboard_admin.html`
Marketplace viewer and collector route map.

## Verification Plan
### Automated Tests
- The backend will lack full-blown unit tests in this MVP, but we will test core endpoints directly using the `run_command` and `curl` to ensure they respond with 200 OK.
- Run `npm run dev` or `python -m uvicorn main:app` and verify there are no startup crashes with the ML dependencies.

### Manual Verification
1. Open the frontend [register.html](file:///c:/Users/USER/OneDrive/Documents/D/recyclex-platform/frontend/register.html) in the browser, fill out the long form as a User, generate OTP (view in terminal), verify, and register.
2. Login as the new User, observe the Profile Dashboard, check that the navigation bar contains "Eco Rewards" and "CO2 Saved".
3. Upload a sample image (e.g. plastic bottle) through the UI and verify the AI Waste Scanner correctly classifies it as Plastic.
4. Register an Admin, login, and verify the Marketplace shows the uploaded scrap and the Route Optimizer computes a distance.
