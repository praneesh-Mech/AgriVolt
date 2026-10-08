# Publish AgriVolt

AgriVolt is ready for a free two-part deployment:

1. Push this folder to a GitHub repository.
2. Create a Python Web Service on Render from that repository. Render reads `render.yaml`.
3. Set the Render environment variable `CORS_ORIGINS` to the final website URL, for example `https://agrivolt.vercel.app`.
4. Create a Vercel project from the `frontend-app` folder.
5. In Vercel, set `VITE_API_URL` to the Render API URL, then deploy.

## Important demo note

The current backend uses SQLite, which is suitable for the hackathon demo. A production deployment needs PostgreSQL or another managed database so readings persist across service restarts.

## Future official features

- Ask for location permission only when the farmer taps a clear location button.
- Store the consent decision and explain why location is needed (weather, local advisories, and field mapping).
- Add phone-number login/OTP, farmer profiles, device pairing, and hardware pump safeguards.
- Require human confirmation for every real pump command; the existing pump controls are demo commands only.
