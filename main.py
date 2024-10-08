import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import pickle
import threading

# File to store the download path
CONFIG_FILE = "config.pkl"

# Global variable to control cancellation
cancel_download = threading.Event()

def load_config():
    """
    Load the saved configuration from a pickle file.
    
    Returns:
        dict: Configuration dictionary with saved settings.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_config(config):
    """
    Save the configuration to a pickle file.
    
    Args:
        config (dict): Configuration dictionary to be saved.
    """
    with open(CONFIG_FILE, 'wb') as f:
        pickle.dump(config, f)

def update_progress_bar(downloaded_bytes, total_bytes):
    """
    Update the progress bar and status label based on the downloaded bytes.
    
    Args:
        downloaded_bytes (int): The number of bytes downloaded.
        total_bytes (int): The total number of bytes to be downloaded.
    """
    if total_bytes > 0:
        progress = (downloaded_bytes / total_bytes) * 100
        progress_var.set(progress)
        root.update_idletasks()

def update_status(message):
    """
    Update the status label with a message.
    
    Args:
        message (str): The message to display on the status label.
    """
    status_label.config(text=message)
    root.update_idletasks()

def progress_hook(d):
    """
    Hook function to handle progress updates and check for cancellation.
    
    Args:
        d (dict): Dictionary containing progress information.
    """
    if cancel_download.is_set():
        raise Exception("Download cancelled")

    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        update_progress_bar(downloaded_bytes, total_bytes)
        message = d.get('info_dict', {}).get('title', 'Downloading...')
        update_status(message)
    elif d['status'] == 'finished':
        update_status(f"Finished downloading: {d['filename']}")
        progress_var.set(100)
        root.update_idletasks()

def download_video():
    """
    Download the video from the provided URL and save it to the selected path.
    """
    url = url_entry.get()
    path = download_path.get()  # Use the saved path
    
    if not url or not path:
        messagebox.showwarning("Input Error", "Please provide both a video URL and a download path.")
        return

    progress_var.set(0)  # Reset progress bar
    update_status("Starting download...")
    cancel_download.clear()  # Clear the cancel event

    def download_task():
        """
        Task to perform the video download using yt_dlp in a separate thread.
        """
        try:
            ydl_opts = {
                'outtmpl': f'{path}/%(title)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',  
                'progress_hooks': [progress_hook]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if not cancel_download.is_set():
                messagebox.showinfo("Success", "Video downloaded successfully!")
                update_status("Download complete!")
        except Exception as e:
            if cancel_download.is_set():
                update_status("Download cancelled.")
            else:
                messagebox.showerror("Error", f"Error downloading video: {e}")
                update_status("Download failed.")
            progress_var.set(0)  # Reset progress bar in case of error

    # Run the download task in a separate thread
    threading.Thread(target=download_task).start()

def download_mp3():
    """
    Download the audio from the provided URL and convert it to MP3 format.
    """
    url = url_entry.get()
    path = download_path.get()  # Use the saved path
    
    if not url or not path:
        messagebox.showwarning("Input Error", "Please provide both a video URL and a download path.")
        return

    progress_var.set(0)  # Reset progress bar
    update_status("Starting download...")
    cancel_download.clear()  # Clear the cancel event

    def download_task():
        """
        Task to perform the audio download and conversion to MP3 using yt_dlp in a separate thread.
        """
        try:
            def hook(d):
                """
                Hook function to handle progress updates and check for cancellation.
                
                Args:
                    d (dict): Dictionary containing progress information.
                """
                if cancel_download.is_set():
                    raise Exception("Download cancelled")
                if d['status'] == 'downloading':
                    total_bytes = d.get('total_bytes', 0)
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    update_progress_bar(downloaded_bytes, total_bytes)
                    message = d.get('info_dict', {}).get('title', 'Downloading...')
                    update_status(message)
                elif d['status'] == 'finished':
                    update_status(f"Finished downloading: {d['filename']}")
                    progress_var.set(100)
                    root.update_idletasks()

            ydl_opts = {
                'outtmpl': f'{path}/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [hook]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if not cancel_download.is_set():
                messagebox.showinfo("Success", "Audio downloaded and converted successfully!")
                update_status("Download and conversion complete!")
        except Exception as e:
            if cancel_download.is_set():
                update_status("Download cancelled.")
            else:
                messagebox.showerror("Error", f"Error downloading or converting audio: {e}")
                update_status("Download or conversion failed.")
            progress_var.set(0)  # Reset progress bar in case of error

    # Run the download task in a separate thread
    threading.Thread(target=download_task).start()

def set_download_path():
    """
    Open a dialog to select a download path and save it.
    """
    path = filedialog.askdirectory()
    if path:
        download_path.set(path)
        save_config({'download_path': path})

def cancel_operation():
    """
    Cancel the ongoing download or conversion.
    """
    cancel_download.set()
    update_status("Cancelling...")
    progress_var.set(0)

# Load saved configuration
config = load_config()
initial_path = config.get('download_path', '')

# Create the GUI
root = tk.Tk()
root.title("Andolon - Youtube Downloader")

# Set window background color and size
root.configure(bg="#2C3E50")
root.geometry("450x460")

# Add custom styles for labels and buttons
tk.Label(root, text="YouTube URL:", bg="#2C3E50", fg="white", font=("Helvetica", 12, "bold")).pack(pady=10)

# Entry field with padding and background color
url_entry = tk.Entry(root, width=40, font=("Helvetica", 10), bg="#ECF0F1", fg="#2C3E50", bd=0)
url_entry.pack(pady=5, ipady=5)

# Download path variable
download_path = tk.StringVar(value=initial_path)

# Entry field for download path with a button to change it
path_entry = tk.Entry(root, textvariable=download_path, width=40, font=("Helvetica", 10), bg="#ECF0F1", fg="#2C3E50", bd=0, state=tk.DISABLED)
path_entry.pack(pady=5, ipady=5)

# Button to change download path
change_path_button = tk.Button(root, text="Change Download Path", bg="#3498DB", fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=10, pady=5, command=set_download_path)
change_path_button.pack(pady=10)

# Styled download button for video
download_button = tk.Button(root, text="Download Video", bg="#E74C3C", fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=20, pady=5, command=download_video)
download_button.pack(pady=5)

# Styled download button for MP3
download_mp3_button = tk.Button(root, text="Download MP3", bg="#E67E22", fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=20, pady=5, command=download_mp3)
download_mp3_button.pack(pady=5)

# Cancel button
cancel_button = tk.Button(root, text="Cancel Operation", bg="#34495E", fg="white", font=("Helvetica", 10, "bold"), relief="flat", padx=20, pady=5, command=cancel_operation)
cancel_button.pack(pady=10)

# Frame for progress bar and status label
progress_frame = tk.Frame(root, bg="#2C3E50")
progress_frame.pack(pady=10, padx=20, fill='x')

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=300)  # Adjust length as needed
progress_bar.pack(pady=5, fill='x')

# Status label with word wrapping
status_label = tk.Label(progress_frame, text="", bg="#2C3E50", fg="white", font=("Helvetica", 8), wraplength=300)
status_label.pack(pady=5)

# Powered by label
powered_by_label = tk.Label(root, text="Powered by Andolon - GitHub Andolon-M", bg="#2C3E50", fg="white", font=("Helvetica", 8))
powered_by_label.pack(side=tk.BOTTOM, pady=5)

# Start the GUI event loop
root.mainloop()
