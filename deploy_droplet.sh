#!/bin/bash

# DigitalOcean Droplet Setup Script for BMM SEO Agent
# Run this on a fresh Ubuntu 22.04 droplet

set -e  # Exit on error

echo "================================================"
echo "BMM SEO Agent - DigitalOcean Droplet Setup"
echo "================================================"
echo ""

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js 20
echo "📦 Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install Git
echo "📦 Installing Git..."
apt install -y git

# Install nginx (for reverse proxy)
echo "🌐 Installing Nginx..."
apt install -y nginx

# Clone repository
echo "📥 Cloning repository..."
cd /opt
git clone https://github.com/areu01or00/SEO-Agent.git bmm-seo-agent
cd bmm-seo-agent

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
npm install -g dataforseo-mcp-server
npm install

# Create .env file
echo "🔧 Creating .env file..."
cat > .env << 'EOF'
# Add your credentials here
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=google/gemini-2.5-flash-lite
EOF

echo "⚠️  IMPORTANT: Edit /opt/bmm-seo-agent/.env with your API credentials!"

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/bmm-seo-agent.service << 'EOF'
[Unit]
Description=BMM SEO Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bmm-seo-agent
Environment="PATH=/opt/bmm-seo-agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/bmm-seo-agent/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx reverse proxy
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/bmm-seo-agent << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/bmm-seo-agent /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl reload nginx

# Enable and start service
echo "🚀 Starting BMM SEO Agent service..."
systemctl daemon-reload
systemctl enable bmm-seo-agent
systemctl start bmm-seo-agent

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Show status
echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📝 Next Steps:"
echo "1. Edit API credentials: nano /opt/bmm-seo-agent/.env"
echo "2. Restart service: systemctl restart bmm-seo-agent"
echo "3. Check status: systemctl status bmm-seo-agent"
echo "4. View logs: journalctl -u bmm-seo-agent -f"
echo ""
echo "🌐 Access your app at: http://YOUR_DROPLET_IP"
echo ""
echo "To get a domain name:"
echo "1. Point your domain's A record to this droplet's IP"
echo "2. Install SSL with: apt install certbot python3-certbot-nginx && certbot --nginx"
echo ""