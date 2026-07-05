import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from config import MONGO_DB

app = Flask(__name__)

@app.route("/")
def welcome():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RestrictBot Server</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                background: radial-gradient(circle, #0f172a, #020617);
                color: #e2e8f0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                padding: 40px;
                border-radius: 16px;
                background: rgba(30, 41, 59, 0.7);
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(to right, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p {
                color: #94a3b8;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Study Bot Server is Active ⚝</h1>
            <p>Powered by 𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡Ｅ ⚝</p>
        </div>
    </body>
    </html>
    """

@app.route("/watch-ad")
def watch_ad():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verify Session</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {
                background: radial-gradient(circle at center, #0f172a, #020617);
                color: #e2e8f0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                overflow: hidden;
            }
            .card {
                text-align: center;
                padding: 30px;
                border-radius: 24px;
                background: rgba(30, 41, 59, 0.45);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                width: 85%;
                max-width: 380px;
                transition: all 0.3s ease;
            }
            h2 {
                font-size: 1.8rem;
                margin-top: 0;
                margin-bottom: 10px;
                font-weight: 700;
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p {
                color: #94a3b8;
                font-size: 0.95rem;
                line-height: 1.5;
                margin-bottom: 25px;
            }
            .timer-box {
                font-size: 3rem;
                font-weight: 800;
                color: #38bdf8;
                margin: 20px 0;
                font-variant-numeric: tabular-nums;
                text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            .btn {
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                color: #ffffff;
                border: none;
                padding: 14px 28px;
                font-size: 1rem;
                font-weight: 600;
                border-radius: 14px;
                cursor: pointer;
                width: 100%;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);
            }
            .btn:disabled {
                background: rgba(255, 255, 255, 0.1);
                color: #64748b;
                cursor: not-allowed;
                box-shadow: none;
            }
            .btn:not(:disabled):hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5);
            }
            .progress-bar {
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 20px;
            }
            .progress-fill {
                height: 100%;
                width: 100%;
                background: linear-gradient(to right, #38bdf8, #818cf8);
                transform: translateX(-100%);
                transition: transform 1s linear;
            }
            .status-msg {
                font-size: 0.85rem;
                color: #10b981;
                margin-top: 15px;
                font-weight: 500;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Ad Verification</h2>
            <p>Please watch the ad below to unlock premium features for 3 hours.</p>
            
            <!-- PLACEHOLDER FOR AD CODE -->
            <!-- Users can paste their Monetag / Adsterra ad codes here -->
            <div id="ad-container" style="min-height: 50px; margin-bottom: 20px;">
                <!-- Ad Placeholder Tag -->
            </div>

            <div class="progress-bar">
                <div id="progress" class="progress-fill"></div>
            </div>

            <div id="timer" class="timer-box">15</div>

            <button id="verify-btn" class="btn" disabled onclick="verifyUser()">
                Waiting for Ad...
            </button>
            <div id="status" class="status-msg">✅ Session verified successfully! Closing...</div>
        </div>

        <script>
            if (window.Telegram && window.Telegram.WebApp) {
                window.Telegram.WebApp.ready();
                window.Telegram.WebApp.expand();
            }

            let timeLeft = 15;
            const timerElement = document.getElementById('timer');
            const progressElement = document.getElementById('progress');
            const verifyBtn = document.getElementById('verify-btn');
            const statusElement = document.getElementById('status');

            const interval = setInterval(() => {
                timeLeft--;
                timerElement.textContent = timeLeft;
                
                const progressPercent = ((15 - timeLeft) / 15) * 100;
                progressElement.style.transform = `translateX(-${100 - progressPercent}%)`;

                if (timeLeft <= 0) {
                    clearInterval(interval);
                    timerElement.style.display = 'none';
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = 'Complete Verification';
                }
            }, 1000);

            async function verifyUser() {
                verifyBtn.disabled = true;
                verifyBtn.textContent = 'Verifying...';

                let userId = null;
                
                if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
                    userId = window.Telegram.WebApp.initDataUnsafe.user.id;
                }

                if (!userId) {
                    const urlParams = new URLSearchParams(window.location.search);
                    userId = urlParams.get('user_id');
                }

                if (!userId) {
                    alert('User ID not found! Please open this page via the Telegram Bot.');
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = 'Complete Verification';
                    return;
                }

                try {
                    const response = await fetch('/api/verify-ad', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ user_id: parseInt(userId) })
                    });

                    const data = await response.json();
                    if (data.success) {
                        statusElement.style.display = 'block';
                        setTimeout(() => {
                            if (window.Telegram && window.Telegram.WebApp) {
                                window.Telegram.WebApp.close();
                            } else {
                                window.close();
                            }
                        }, 1500);
                    } else {
                        alert('Verification failed: ' + (data.error || 'Unknown error'));
                        verifyBtn.disabled = false;
                        verifyBtn.textContent = 'Complete Verification';
                    }
                } catch (error) {
                    alert('Error connecting to verification server: ' + error.message);
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = 'Complete Verification';
                }
            }
        </script>
    </body>
    </html>
    """

@app.route("/api/verify-ad", methods=["POST"])
def verify_ad():
    try:
        data = request.get_json()
        if not data or "user_id" not in data:
            return jsonify({"success": False, "error": "Missing user_id"}), 400
        
        user_id = int(data["user_id"])
        
        # Generate a random token param
        import random, string
        param = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Connect to MongoDB synchronously
        client = MongoClient(MONGO_DB)
        db = client["telegram_bot"]
        token_collection = db["tokens"]
        
        # Upsert verification token
        token_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "param": param,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(hours=3)
                }
            },
            upsert=True
        )
        client.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
