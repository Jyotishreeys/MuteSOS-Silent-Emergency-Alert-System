\# 🚨 MuteSOS – Silent Emergency Alert System



> An intelligent Django-based emergency alert system designed to \\\*\\\*silently protect individuals in distress\\\*\\\* through hidden triggers, AI voice tone detection, and instant multi-channel alerts.



---



\## 🌟 Overview



\*\*MuteSOS\*\* is a cutting-edge emergency response web application that empowers users to send \*\*SOS alerts silently\*\* when they feel threatened — without drawing attention.

It integrates \*\*AI-based danger tone detection\*\*, \*\*SMS/Voice/Email alerts\*\*, \*\*trusted contacts\*\*, and \*\*Progressive Web App (PWA)\*\* support for mobile accessibility — all wrapped in a professional, blue-themed Django web interface.



This project was developed as an \*\*MCA Final Year Major Project\*\*, combining modern web technologies, artificial intelligence, and real-world safety applications.



---



\## 🔐 Key Features



| Category | Description |

|-----------|--------------|

| 🆘 \*\*Silent SOS Triggers\*\* | Allows users to trigger an emergency alert secretly using predefined actions, buttons, or voice activation. |

| 🧠 \*\*AI Voice Tone Detection\*\* | Uses machine learning models to analyze voice tone and detect distress automatically. |

| 📞 \*\*Twilio Integration\*\* | Sends real-time \*\*SMS, voice calls, and emails\*\* to all trusted contacts when SOS is triggered. |

| 👩‍👩‍👧 \*\*Trusted Contacts Module\*\* | Users can add and manage personal emergency contacts, who are instantly alerted during emergencies. |

| 🛰️ \*\*Live Tracking (optional)\*\* | Shares real-time location details via Google Maps API during active alerts. |

| 💬 \*\*Fake Exit Message\*\* | Allows users to safely close the system with a fake neutral message (to disguise the SOS action). |

| 🌐 \*\*Progressive Web App (PWA)\*\* | Fully installable and mobile-friendly — works offline and can be added to the home screen. |

| 🎨 \*\*Blue-Themed UI\*\* | Polished and professional design built with HTML, CSS, and Django templates. |



---



\## 🧩 System Modules



1\. \*\*Home \& Dashboard Module\*\*

   - Displays all core features.

   - Integrated with global base template and navigation.

2\. \*\*User System (Login, Register, Profile)\*\*

   - Role-based access for Victims and Trusted Contacts.

3\. \*\*SOS Trigger Module\*\*

   - AI-based distress analysis.

   - Sends SMS, Email, and Voice call alerts.

4\. \*\*Trusted Contacts \& Emergency Helplines\*\*

   - Editable user contacts.

   - Predefined national helplines (Police, Women Helpline, etc.).

5\. \*\*PWA Integration\*\*

   - Service Worker, Manifest, and offline caching for app-like experience.



---



\## 🧠 AI Feature



MuteSOS includes a lightweight \*\*AI danger tone detection system\*\* trained to identify stress or distress in recorded voice samples.

If distress is detected:

\- An SOS is triggered automatically.

\- Alerts are sent to all trusted contacts.

\- System optionally activates voice call \& live location features.



---



\## 🛠️ Tech Stack



| Layer | Technology |

|--------|-------------|

| \*\*Frontend\*\* | HTML5, CSS3, JavaScript |

| \*\*Backend\*\* | Django (Python Framework) |

| \*\*Database\*\* | SQLite3 |

| \*\*AI/ML\*\* | TensorFlow / Librosa / Scikit-learn (for voice tone analysis) |

| \*\*Communication\*\* | Twilio API (SMS, Voice, Email) |

| \*\*Environment Management\*\* | `.env` for credentials (Gmail, Twilio) |

| \*\*Deployment\*\* | Render / GitHub / Localhost |



---



\## ⚙️ Installation \& Setup



\### 1️⃣ Clone the repository

```bash

git clone https://github.com/<your-username>/MuteSOS-Silent-Emergency-Alert-System.git

cd MuteSOS-Silent-Emergency-Alert-System





Create a virtual environment

python -m venv venv

venv\\\\Scripts\\\\activate



Install dependencies

pip install -r requirements.txt



Run database migrations

python manage.py makemigrations

python manage.py migrate




🧪 Future Enhancements

Live video stream or emergency camera capture.

AI-based image recognition for threat detection.

Integration with GPS devices or smartwatches.

Support for multilingual emergency alerts.


📚 Project Type

🎓 MCA Final Year Major Project
🧑‍💻 Built using Python + Django + AI + PWA

💙 Developed By

👩‍💻 Jyotishree S

MCA Student | Full Stack Developer | AI Enthusiast

🔗 GitHub Profile: https://github.com/Jyotishreeys

✉️ Email: jyotishree@gmail.com

Acknowledgements

Special thanks to:

Twilio API for providing SMS & Voice capabilities.

Django community for their robust framework support.

Mentors & Faculty for project guidance.


📜 License:

This project is licensed under the MIT License — feel free to fork, modify, and build upon it with attribution.