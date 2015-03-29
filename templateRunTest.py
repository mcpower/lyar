import engine.template as template

from tornado.ncss import Server


# Define a function which returns the HTML for a page.
def index(response):
    response.write(template.render_page(
        "templateTest.html",
        {"foo": "I'm foo", "bar": "lol", "n": 3}
    ))

# Make a server object so we can attach URLs to functions.
server = Server()

# This says that localhost:8888/ should display the result of the
# "index" function.
server.register("/", index)

# Start the server. Gotta do this.
server.run()
