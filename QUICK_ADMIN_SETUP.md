# Quick Admin Setup (Railway 2025)

Since Railway removed the Shell/Terminal tab, here are the **easiest** ways to create your admin account:

---

## ✅ METHOD 1: Temporarily Modify Start Command (Easiest!)

### Step 1: Go to Railway Dashboard
1. Visit https://railway.app/dashboard
2. Click your **backend service**
3. Go to **Settings** tab

### Step 2: Update Start Command
Find the **Start Command** setting and **temporarily** change it to:

```bash
python create_admin.py && bash railway_start.sh
```

This will:
- Create the admin account first
- Then start your app normally

### Step 3: Deploy
Click **Save** and let Railway redeploy (automatic)

### Step 4: Check Logs
1. Go to **Deployments** tab
2. Click the latest deployment
3. Look for this output:
   ```
   🎉 Admin account created successfully!
   📧 Email: admin@gradgen.ai
   🔑 Password: admin123
   ```

### Step 5: Revert Start Command
**Important!** Once you see the account created, go back to Settings and change the start command back to:

```bash
bash railway_start.sh
```

Save and redeploy.

**Done!** You now have an admin account.

---

## ✅ METHOD 2: Use Railway CLI Locally (If You Want)

### Step 1: Login to Railway
```bash
railway login
```

This will open your browser for authentication.

### Step 2: Link to Your Project
```bash
cd /path/to/tanghouse
railway link
```

Select your GradGen project.

### Step 3: Run the Script
```bash
cd webapp/backend
railway run python create_admin.py
```

This runs the script **locally** but with Railway's database connection.

**Custom email/password:**
```bash
railway run python create_admin.py your@email.com YourPassword "Your Name"
```

---

## ✅ METHOD 3: Direct Database Access (Advanced)

### Get Database URL
1. Go to Railway dashboard
2. Click your **PostgreSQL** service
3. Go to **Variables** tab
4. Copy the `DATABASE_URL`

### Run Script Locally
```bash
cd webapp/backend
export DATABASE_URL="postgresql://..."  # Paste your URL
python create_admin.py
```

---

## 🎯 Default Admin Credentials

After running any method above, you'll have:

```
Email: admin@gradgen.ai
Password: admin123
Status: ✅ Verified, ✅ Superuser, ✅ Free Tier Available
```

---

## 🧪 Test the Account

### 1. Login
Go to https://www.gradgen.ai/login and use:
- Email: `admin@gradgen.ai`
- Password: `admin123`

### 2. Test Free Tier
- Upload a photo
- Generate 5 watermarked photos
- Check they have **prominent watermarks**

### 3. Test Premium Upgrade
- Try to generate again → See pricing modal
- Use Stripe test card: `4242 4242 4242 4242`
- Complete payment
- Generate 5 more premium photos
- Download all 10 without watermarks

---

## 🔧 Troubleshooting

### "User already exists"
✅ Perfect! The account exists. Just use the credentials above.

### Can't find Start Command in Settings
- Look for "Service Settings" or "Deploy Settings"
- Might be under "Custom Start Command"

### Railway CLI login fails
- Make sure you have a browser available
- Try `railway whoami` to check if already logged in

### Script runs but no output
- Check the deployment logs carefully
- Look for the 🎉 emoji in the logs

---

## 💡 Recommended: Method 1

**Method 1 (temporary start command)** is the easiest because:
- ✅ No CLI installation needed
- ✅ No local setup required
- ✅ Works from any device
- ✅ Just a few clicks in Railway dashboard

It takes less than 2 minutes! 🚀
