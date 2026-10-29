# Hokie Job Tracker

A React web app for Virginia Tech students to track job applications, browse upcoming career fairs, and set reminders.

## Run it

```bash
npm install
npm run dev
```

Then open the URL Vite prints (usually http://localhost:5173).

## Structure

```
src/
  App.jsx                 Routes: / (sign in), /dashboard, /applications, /fairs, /reminders
  data.js                 Sample data — replace with your API
  styles.css              Design tokens (VT maroon/orange) and all styles
  utils/dates.js          Date parsing, formatting and reminder grouping
  components/
    AppLayout.jsx         Sidebar + page shell; holds app state and shares it via outlet context
    Sidebar.jsx           Main navigation
    Icon.jsx              Inline stroke icons
    StatusBadge.jsx       Applied / Interview / Offer / Rejected pill
    FilterPills.jsx       Toggle-pill filter row
    CompanyAvatar.jsx     Company initial tile
    DateBlock.jsx         Month/day calendar tile
  pages/
    Login.jsx
    Dashboard.jsx
    Applications.jsx      Status filter, search, add-application form
    CareerFairs.jsx       In person / virtual / going filters; "I'm going" adds a reminder
    Reminders.jsx         Grouped checklist + new-reminder form
```

## Next steps

- Hook sign-in up to VT CAS / SSO (see `pages/Login.jsx`).
- Replace the `useState` seeds in `components/AppLayout.jsx` with data from your backend.
- Load the real career-fair schedule from VT Career Services (names, dates and employer counts in `data.js` are placeholders).
- Send reminder notifications (email / browser) from the backend using each reminder's `notify` settings.
