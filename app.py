from main import create_app

app = create_app(demo=True, err_handler=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)