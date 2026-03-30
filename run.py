import uvicorn

if __name__ == "__main__":
    print("🦷 Starting Bright Smile Dental Clinic AI Assistant...")
    print("🌐 Open your browser at: http://127.0.0.1:8000")
    print("📚 API docs at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)