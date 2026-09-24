# Smart Hospital Finder & Emergency Healthcare Platform

Modular Django + Tailwind stack for **GPS hospital discovery**, **bed polling**, **appointments with Stripe**, **emergency nearest-ER flow**, **hospital admin dashboards**, **rule-based chatbot**, and **email notifications**.

## Quick start (local)

```bash
cd "The HTML"
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # optional: set keys
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser   # optional: platform superuser
python manage.py runserver
```

- **Patients**: register at `/accounts/register/` (default role: patient).
- **Demo logins** (after `seed_demo`): `demo_patient` / `demo12345`, `hospital_admin` / `demo12345`, `dr_kumar` / `demo12345`.
- **Django admin**: `/admin/` for full CRUD on hospitals, doctors, schedules.

## Environment variables

See `.env.example`. Important keys:

| Variable                                 | Purpose                                            |
| ---------------------------------------- | -------------------------------------------------- |
| `USE_POSTGRES=true` + `POSTGRES_*`       | Production DB (otherwise SQLite)                   |
| `GOOGLE_MAPS_API_KEY`                    | Maps on search, hospital detail, emergency results |
| `STRIPE_SECRET_KEY`, `STRIPE_PUBLIC_KEY` | Checkout + verification                            |
| `STRIPE_WEBHOOK_SECRET`                  | Production payment confirmation                    |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP (defaults to console email if unset)          |

## REST API (session auth)

Base path: `/api/`. For browser or SPA clients using cookies, call `GET /api/csrf/` first, then send `X-CSRFToken` on unsafe methods.

| Method | Path                                                                             | Description                                                 |
| ------ | -------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| POST   | `/api/register/`                                                                 | Create patient user + session                               |
| POST   | `/api/login/`                                                                    | `username`, `password`                                      |
| GET    | `/api/hospitals/nearby/?lat=&lng=&department=&min_rating=&emergency=1&min_beds=` | Discovery                                                   |
| GET    | `/api/hospitals/<id>/`                                                           | Hospital detail                                             |
| GET    | `/api/hospitals/<id>/resources/`                                                 | Bed/equipment JSON (polling)                                |
| GET    | `/api/doctors/<hospital_id>/`                                                    | Doctors in hospital                                         |
| GET    | `/api/emergency/nearest/?lat=&lng=`                                              | Top 3 ER hospitals                                          |
| POST   | `/api/appointments/book/`                                                        | JSON: `doctor_id`, `department_id`, `scheduled_at`, `notes` |
| GET    | `/api/appointments/user/`                                                        | Current user’s appointments                                 |
| POST   | `/api/payment/`                                                                  | `{"appointment_id": N}` → `checkout_url` or message         |

## Payments

1. Book appointment → status `pending_payment`.
2. **Pay now** (UI) or `POST /api/payment/` returns Stripe Checkout URL.
3. Success URL `/payments/stripe/success/` marks payment succeeded and sets status to `pending_approval`.
4. Hospital admin **approves** in `/hospital-admin/appointments/` → `confirmed`.

**DEBUG without Stripe**: use **Demo pay** on appointment history (or `/payments/demo/<id>/`).

Configure webhook in Stripe Dashboard → endpoint `https://<host>/payments/stripe/webhook/` with signing secret in `STRIPE_WEBHOOK_SECRET`.

## Google Maps

Create a Maps JavaScript API key in Google Cloud; restrict by HTTP referrer for your domain. Set `GOOGLE_MAPS_API_KEY` in `.env`.

## Realtime beds

Hospital detail page polls `/api/hospitals/<id>/resources/` every **8 seconds** (upgrade path: WebSockets + Channels).

## Chatbot

`POST /chatbot/message/` with JSON `{"message":"..."}` returns `reply` and optional `actions` (links). Rule engine lives in `chatbot/views.py`.

## Deployment (Render / Railway)

1. **Build**: Python 3.12+, `pip install -r requirements.txt`, `python manage.py collectstatic --noinput`, `python manage.py migrate`.
2. **Start**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` (add `gunicorn` to `requirements.txt` for production).
3. **Env**: set `DEBUG=False`, `ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, database URL vars, `STRIPE_*`, `GOOGLE_MAPS_API_KEY`, email SMTP.
4. **Static**: WhiteNoise serves `STATIC_ROOT` (`staticfiles/`).
5. **HTTPS**: enable `SECURE_SSL_REDIRECT` behind TLS-terminating proxy if desired.

### Render example

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Railway example

- Add PostgreSQL plugin, map env vars to `USE_POSTGRES=true` and `POSTGRES_*`, set `PORT` for gunicorn.

## Razorpay (future)

Stripe is implemented end-to-end. For Razorpay, mirror `payments/services.py` with order creation and verify signature in a webhook view; store provider `razorpay` on `Payment`.

## SMS (future)

Twilio env vars are reserved in `.env.example`; wire `notifications/services.py` to send SMS on `EMERGENCY_ALERT` kinds.

## Security notes

- Passwords hashed via Django’s default (PBKDF2).
- CSRF on all form posts; DRF session auth enforces CSRF for unsafe API calls from the browser.
- Do not commit `.env`; rotate `DJANGO_SECRET_KEY` and Stripe keys for production.

## Project layout

- `accounts/` — custom `User`, `PatientProfile`, registration/profile.
- `hospitals/` — `Hospital`, `Department`, `Doctor`, `DoctorSchedule`, `HospitalResources`, discovery services, admin UI.
- `appointments/` — booking, history, cancel/reschedule, slot service.
- `payments/` — Stripe Checkout, webhook, demo pay.
- `notifications/` — in-app + email helper.
- `chatbot/` — rule-based assistant.
- `api/` — DRF JSON endpoints.
- `templates/`, `static/` — Tailwind (CDN) + JS (maps, polling, chatbot).

---

Built for a **36-hour hackathon**: swap SQLite for PostgreSQL, plug in real SMTP/SMS, and harden keys before production.
