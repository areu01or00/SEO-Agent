#!/bin/bash

# BMM SEO Agent Deployment Script
# Supports multiple deployment methods

echo "🚀 BMM SEO Agent Deployment Tool"
echo "================================="
echo ""
echo "Select deployment method:"
echo "1) Streamlit Cloud (Free, Public)"
echo "2) Local Network Server"
echo "3) Docker Container"
echo "4) Cloud VPS Setup"
echo "5) Password-Protected Local"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "📦 Preparing for Streamlit Cloud deployment..."
        
        # Create .streamlit/config.toml for deployment settings
        mkdir -p .streamlit
        cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 10
enableCORS = false
EOF
        
        # Create secrets.toml template
        cat > .streamlit/secrets.toml.example << 'EOF'
# Rename to secrets.toml and add to Streamlit Cloud
DATAFORSEO_USERNAME = "your_username"
DATAFORSEO_PASSWORD = "your_password"
OPENROUTER_API_KEY = "your_key"
OPENROUTER_MODEL = "google/gemini-2.0-flash-001"
EOF
        
        echo "✅ Streamlit Cloud preparation complete!"
        echo ""
        echo "Next steps:"
        echo "1. Push code to GitHub"
        echo "2. Visit https://share.streamlit.io"
        echo "3. Connect your GitHub repo"
        echo "4. Add secrets from secrets.toml.example"
        echo "5. Deploy!"
        ;;
        
    2)
        echo "🏢 Setting up Local Network Server..."
        
        # Create systemd service for auto-start
        cat > bmm-seo-agent.service << 'EOF'
[Unit]
Description=BMM SEO Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Downloads/Keyword agent
Environment="PATH=/home/$USER/Downloads/Keyword agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/$USER/Downloads/Keyword agent/venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        
        echo "✅ Service file created!"
        echo ""
        echo "To install as system service:"
        echo "sudo cp bmm-seo-agent.service /etc/systemd/system/"
        echo "sudo systemctl enable bmm-seo-agent"
        echo "sudo systemctl start bmm-seo-agent"
        echo ""
        echo "Access at: http://$(hostname -I | cut -d' ' -f1):8501"
        ;;
        
    3)
        echo "🐳 Creating Docker deployment..."
        
        # Create Dockerfile
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install MCP server
RUN npm install -g dataforseo-mcp-server

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
        
        # Create docker-compose.yml
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  bmm-seo-agent:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATAFORSEO_USERNAME=${DATAFORSEO_USERNAME}
      - DATAFORSEO_PASSWORD=${DATAFORSEO_PASSWORD}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_MODEL=${OPENROUTER_MODEL:-google/gemini-2.5-flash-lite}
    volumes:
      - ./data:/app/data  # For persistent storage if needed
    restart: unless-stopped
EOF
        
        echo "✅ Docker files created!"
        echo ""
        echo "To deploy with Docker:"
        echo "docker-compose up -d"
        echo ""
        echo "Or build and run manually:"
        echo "docker build -t bmm-seo-agent ."
        echo "docker run -p 8501:8501 --env-file .env bmm-seo-agent"
        ;;
        
    4)
        echo "☁️ Cloud VPS Setup Script..."
        
        # Create setup script for VPS
        cat > setup_vps.sh << 'EOF'
#!/bin/bash

# BMM SEO Agent VPS Setup Script
# Run this on Ubuntu/Debian VPS

echo "Setting up BMM SEO Agent on VPS..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nodejs npm git nginx certbot python3-certbot-nginx

# Clone repository (replace with your repo)
git clone https://github.com/yourusername/bmm-seo-agent.git
cd bmm-seo-agent

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install MCP server
sudo npm install -g dataforseo-mcp-server

# Create systemd service
sudo tee /etc/systemd/system/bmm-seo-agent.service > /dev/null <<'SERVICE'
[Unit]
Description=BMM SEO Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bmm-seo-agent
Environment="PATH=/home/ubuntu/bmm-seo-agent/venv/bin:/usr/bin"
ExecStart=/home/ubuntu/bmm-seo-agent/venv/bin/streamlit run app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Setup Nginx reverse proxy
sudo tee /etc/nginx/sites-available/bmm-seo-agent > /dev/null <<'NGINX'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

# Enable site
sudo ln -s /etc/nginx/sites-available/bmm-seo-agent /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Start service
sudo systemctl enable bmm-seo-agent
sudo systemctl start bmm-seo-agent

echo "✅ VPS setup complete!"
echo "Add SSL with: sudo certbot --nginx -d your-domain.com"
EOF
        
        chmod +x setup_vps.sh
        echo "✅ VPS setup script created!"
        echo ""
        echo "Copy setup_vps.sh to your VPS and run it"
        ;;
        
    5)
        echo "🔒 Password-Protected Local Setup..."
        
        # Create auth file
        cat > auth_config.py << 'EOF'
import streamlit as st
import hashlib
import os

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == os.getenv("APP_PASSWORD_HASH", "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"):  # default: "password"
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True
EOF
        
        echo "✅ Password protection setup created!"
        echo ""
        echo "To use password protection:"
        echo "1. Add 'from auth_config import check_password' to app.py"
        echo "2. Add 'if not check_password(): st.stop()' at the beginning of app.py"
        echo "3. Set APP_PASSWORD_HASH environment variable with SHA256 hash of your password"
        echo ""
        echo "Generate password hash with:"
        echo "python -c \"import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())\""
        ;;
esac

echo ""
echo "📌 General deployment tips:"
echo "- Always use environment variables for secrets"
echo "- Consider adding basic auth for internal tools"
echo "- Use HTTPS in production (Let's Encrypt for free SSL)"
echo "- Monitor with tools like UptimeRobot (free tier available)"