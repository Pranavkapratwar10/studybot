#!/bin/bash
echo "Starting Admin Panel..."
echo ""
echo "Admin Panel will open in your browser"
echo "Login with:"
echo "  Username: admin"
echo "  Password: 826282"
echo ""
source venv/bin/activate
streamlit run admin/admin_panel.py --server.port=8502
