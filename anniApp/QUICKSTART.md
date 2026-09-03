# Quick Start Guide

Get your anniversary app running in minutes!

## Step 1: Setup MySQL Database

```bash
mysql -u root -p
CREATE DATABASE anniversary_app;
EXIT;
```

## Step 2: Configure Environment

```bash
# Copy environment files
cp .env.example .env
cd frontend && cp .env.example .env && cd ..

# Edit .env and update your MySQL password
# DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/anniversary_app
```

## Step 3: Install Dependencies

```bash
# Install backend dependencies
poetry install

# Install frontend dependencies
cd frontend && npm install && cd ..
```

## Step 4: Seed Database

```bash
# Load sample activities into database
poetry run python -m backend.app.seed_data
```

## Step 5: Run the App

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
bash run.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 6: Use the App

- **Guest Access**: http://localhost:5173
- **Admin Results**: http://localhost:5173/anniversary-celebration-results

That's it! Your anniversary voting app is ready! 🎉

## Customizing Activities

Edit `backend/app/seed_data.py` to change the questions and voting options, then:

```bash
# Drop and recreate database
mysql -u root -p
DROP DATABASE anniversary_app;
CREATE DATABASE anniversary_app;
EXIT;

# Re-seed with your custom data
poetry run python -m backend.app.seed_data
```

## Troubleshooting

**Can't connect to database?**
- Check MySQL is running: `sudo service mysql status`
- Verify credentials in `.env` file
- Make sure database exists: `SHOW DATABASES;` in MySQL

**Frontend won't connect to backend?**
- Check backend is running on port 8000
- Verify `VITE_API_URL` in `frontend/.env`
- Check for CORS errors in browser console

**Port already in use?**
- Backend: Change port in `backend/run.sh`
- Frontend: Vite will auto-increment to next available port

Need more help? Check the full README.md
