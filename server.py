from src.app import create_app

if __name__ == "__main__":
    app, app_wrapper = create_app()
    # CAUTION use_reloader=False is to avoid reloading the app and creating a new
    # thread for the pika connection.
    app_wrapper.run(app=app, host="0.0.0.0", debug=True, use_reloader=False)
