import os
# import socket

from app import create_app
app = create_app()
if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        # socket.getaddrinfo('gamerock', 5000)
        app.run(debug=True, host='localhost', port=port)
        
        