from main import create_app

app = create_app(demo=True, err_handler=True)

if __name__ == '__main__':
    app.run() 