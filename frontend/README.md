# edhub frontend — react + vite + tailwind + shadcn/ui

this is the frontend part of the edhub lms system. it is built with react (vite), styled using tailwind css, and powered by shadcn/ui component system.

---

## 🚀 getting started

### 1. install dependencies

```bash
cd frontend
npm install
```

### 2. start development server

```bash
npm run dev
```

app will be running at: http://localhost:5173

### 📁 project structure

```bash
frontend/
├── src/
│   ├── components/       # reusable components (ui + layout)
│   ├── pages/            # route-level views
│   ├── lib/              # api and utils
│   ├── App.jsx
│   └── main.jsx
├── index.css             # global tailwind + base styles
├── tailwind.config.js
├── postcss.config.js
└── jsconfig.json         # alias config for `@/`
```

### 🎨 using shadcn/ui components

to add a component (e.g., button, input):

```bash
npx shadcn add button
npx shadcn add input
```

use like this:

```jsx
import { Button } from "@/components/ui/button";

<Button className="w-full">click me</Button>
```

you can customize every component using tailwind utility classes.
