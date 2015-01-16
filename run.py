from tornado.ncss import Server
import engine.template as template
import db.api as api
import re


username_regex = re.compile(r"^[a-zA-Z0-9\-_]{3,20}$")
password_regex = re.compile(r"^[ -~]{1,128}$")

def not_mine(userid, questid):
    return userid != api.Question.find(questid).creator_id

def is_disabled(userid, questid):
    all_votes = api.Vote.find_all(voter_id=userid, qid=questid)
    if any(userid == vote.voter_id for vote in all_votes) or not not_mine(userid, questid):
        return "disabled"
    else:
        return " "

def is_checked(userid, questid, vote):
    user_vote = api.Vote.find_all(qid=questid, voter_id=userid)
    if len(user_vote) > 0 and str(user_vote[0].vote) == str(vote):
        return True
    else:
        return False

def page_not_found(response):
    response.redirect("/404")

def _404(response):
    current_user = get_user_from_response(response)
    response.write(template.render_page("404.html", {
        "questions" : api.Question.find_all(),
        "current_user": current_user
    }))
    
def about(response):
    current_user = get_user_from_response(response)
    response.write(template.render_page("about.html", {
        "questions" : api.Question.find_all(),
        "current_user": current_user
    }))

def view_question(response):
    current_user = get_user_from_response(response)
    if current_user is None:
        # to do: redirect to new user index page (splash.html... I think)
        response.redirect("/login")
    else:
        context = {
            "questions": api.Question.find_all_home_specific(),
            "count_votes": count_votes,
            "current_user": current_user,
            "message": None,
            'is_checked': is_checked,
            'is_disabled' : is_disabled,
            'not_mine': not_mine
        }
        response.write(template.render_page("q_view.html", context))

def create_question(response):
    current_user = get_user_from_response(response)
    response.write(template.render_page("q_create.html", {
        "message": None,
        "current_user": current_user,
        "statement0" : '',
        "statement1" : '',
        "statement2" : '' ,
        "name" : ''
    }))

def insert_new_question(response):
    # recieves data from sent form and redirects to viewing new question
    current_user = get_user_from_response(response)
    name = response.get_field("name").strip()
    statement0 = response.get_field("statement_one").strip()
    statement1 = response.get_field("statement_two").strip()
    statement2 = response.get_field("statement_three").strip()

    fields = [statement0, statement1, statement2, name]

    # checks whether the user manually got to this page by URL editing
    if any(field is None for field in fields) or current_user is None:
        response.redirect('/')
        return # replace this with an else later, I'm kinda lazy -Michael

    error_message = None
    if any(statement == "" for statement in (fields)):
        error_message = 'Please enter 3 non-empty statements and a non-empty topic'
    elif any(len(statement) > 128 for statement in (fields)):
        error_message = 'Character limit exceeded 128 characters'
    elif name == "":
        error_message = 'Please enter question name'
    elif statement0 == statement1 or statement1 == statement2 or statement0 == statement2:
        error_message = 'Please enter 3 different statements'

    if error_message is None:
        lie = response.get_field("lie")
        user_id = get_user_from_response(response).uid # the id of the user
        name = response.get_field("name").strip() # the name of the question
        api.Question.create(statement0, statement1, statement2, lie, user_id, name)
        response.redirect("/")
    else:
        response.write(template.render_page("q_create.html", {
            "message" : error_message,
            "current_user": current_user,
            "statement0": statement0,
            "statement1" : statement1,
            "statement2" : statement2,
            "name": name
        }))

def login(response):
    current_user = get_user_from_response(response)
    if current_user is not None:
        response.write(template.render_page("q_view.html", {
            "questions" : api.Question.find_all(),
            "count_votes": count_votes,
            "current_user": current_user,
            "message":'You are already logged in!'
        }))
        return

    username = response.get_field("username")
    password = response.get_field("password")

    if username is None or password is None:
        response.write(template.render_page("login.html", {
            "message": None,
            "current_user": current_user
        }))
        return

    user = api.User.find(username)
    if user is not None and api.User.hash_password(password) == user.password:
        print("Login successful.")
        response.set_secure_cookie("user_id", str(user.uid))
        response.redirect("/")    
    else:
        print("Login failed. Incorrect username or password.")
        response.write(template.render_page("login.html", {
            "message": "Username or password incorrect.",
            "current_user": current_user
        }))

def logout(response):
    response.clear_cookie("user_id")
    # response.write("You have logged out.")
    response.redirect("/")

# Input: Response object
# Output: Current User object from response or None
# tl;dr: put this in any function:
# current_user = get_user_from_response(response)
def get_user_from_response(response):
    user_id = response.get_secure_cookie("user_id")
    if user_id is None:
        return None
    else:
        return api.User.find(uid=int(user_id))

def register(response):
    current_user = get_user_from_response(response)
    if current_user is not None:
        response.write(template.render_page("q_view.html", {
            "questions" : api.Question.find_all(),
            "count_votes": count_votes,
            "current_user": current_user,
            "message":'You are already logged in!'
        }))
        return

    username = response.get_field("username")
    password = response.get_field("password")
    confirm_password = response.get_field("confirm_password")
    
    if username is None or password is None or confirm_password is None:
        response.write(template.render_page("register.html", {
            'message': None,
            "current_user": current_user
        }))
        return

    error_message = None
    if username == '' or password == '' or confirm_password == '':
        error_message = 'Username or password was empty!'
    elif api.User.find(username):
        error_message = 'Username is taken already!'
    elif password != confirm_password:
        error_message = 'Passwords do not match!'
    elif re.match(username_regex, username) is None:
        error_message = 'Usernames must be between 3 to 16 characters in length and must have alphanumeric characters, dashes or underscores.'
    elif re.match(password_regex, password) is None:
        error_message = 'Passwords must be between 1 to 128 characters in length and must have printable ASCII characters.'
    
    if error_message is None:
        user = api.User.create(username, api.User.hash_password(password).decode("ascii"))
        response.set_secure_cookie("user_id", str(user.uid))
        response.redirect("/")
    else:
        response.write(template.render_page("register.html", {
            'message': error_message,
            "current_user": current_user
        }))
        


# check whether the selection is the lie
def vote(response):
    if response.get_field('id') is None:
        response.redirect('/')
        return

    user_input = response.get_field("user_input")
    question_id = int(response.get_field("id"))
    question = api.Question.find(question_id)
    current_user = get_user_from_response(response)
          
    if current_user.uid == question.creator_id:
        response.write(template.render_page("q_view.html", {
            "questions": api.Question.find_all(),
            "count_votes": count_votes,
            "current_user": current_user,
            "message":'You cannot vote on the question. (You are the author)'
        }))
    elif current_user is not None and len(api.Vote.find_all(qid = question_id, voter_id = current_user.uid)) == 0:
        vote = api.Vote.create(question_id, int(user_input), current_user.uid)
        response.redirect('/question/' + str(question_id))
        print(vote.vote)
        print(question.lie)
        if vote.vote == question.lie:
            question_correct_votes = len(api.Vote.find_all(qid = question.qid, vote = question.lie))
            points_to_add = 20 - min(question_correct_votes, 10)
            print(points_to_add)
            current_user.add_points(points_to_add)
    else:
        response.write(template.render_page("q_view.html", {
            "questions" : api.Question.find_all(),
            "count_votes": count_votes,
            "current_user": current_user,
            "message":'You have already voted!'
        }))
        

def count_votes(question_id):
    votes = [len(api.Vote.find_all(question_id, vote=num)) for num in range(3)]
    total = sum(votes)
    return total


def question_handler(response, question_id):
    # the regex ensures that the question_id can't be negative
    current_user = get_user_from_response(response)
    if current_user is None:
        # user is not logged in
        response.redirect('/login')
        return

    question_id = int(question_id)
    question = api.Question.find(question_id)
    if question is None:
        response.write(template.render_page("q_view.html", {
            "questions": api.Question.find_all(),
            "count_votes": count_votes,
            "current_user": current_user,
            "message":'Invalid Question ID!'
        }))
        return
    question_author = question.get_creator()
    
    # only display the voting results if the user has voted
    context =  {
        'pageName': 'View Post',
        "question" : question,
        "current_user": current_user,
        "count_votes": count_votes,
        "author": question_author,
        'disabled': ''
    }
    if len(api.Vote.find_all(qid = question_id, voter_id = current_user.uid)) > 0:
        # count the votes for the statements and store
        votes = [len(api.Vote.find_all(question_id, vote=num)) for num in range(3)]
        total = sum(votes)

        scores = [str(round((vote / total)*100)) for vote in votes]

        context["voted"] = True
        current_vote = api.Vote.find_all(qid = question_id, voter_id = current_user.uid)[0]
        context["vote"] = current_vote
        context["scores"] = scores
    else:
        # user is logged in but has not voted
        context["voted"] = False
    print(context)
    response.write(template.render_page("q_individual.html", context ))


def profile_handler(response, user_name): 
    current_user = get_user_from_response(response)
    user_profile = api.User.find(user_name)
    if user_profile is not None:
        print(user_name)
        print(user_profile)
        response.write(template.render_page('profile.html', {
            'username' : user_profile.username, 
            "questions" : api.Question.find_all(user_profile.uid), 
            "current_user": current_user, 
            "points": user_profile.points
        }))
    else:
        response.redirect('/404')


def statistics_handler(response):
    current_user = get_user_from_response(response)
    response.write(template.render_page('statistics.html', {
        "number_of_votes": len(api.Vote.find_all()),
        "number_of_correct_votes": api.Vote.number_of_correct_votes(),
        "number_of_questions": len(api.Question.find_all()),
        "current_user": current_user
    }))

def scoreboard_handler(response):
    current_user = get_user_from_response(response)
    top_users = api.User.find_best(10)
    response.write(template.render_page('scoreboard.html', {
        "top_users": top_users,
        "current_user": current_user
    }))
    

# Make a server object so we can attach URLs to functions.
server = Server()

# This says that localhost:8888/ should display the result of the
# "index" function.
# server.register("/", index)
server.register("/", view_question)
server.register("/about", about)
server.register("/question/create", create_question)
server.register("/question/insert", insert_new_question)
server.register("/login", login)
server.register("/logout", logout)
server.register("/register", register)
server.register("/question/answer",vote)
server.register(r"/question/(\d+)", question_handler)
server.register(r'/profile/(\w+)', profile_handler)
server.register("/stats", statistics_handler)
server.register("/scoreboard", scoreboard_handler)
server.register("/404", _404)
server.register(r"/.+", page_not_found) 
# Start the server. Gotta do this.
server.run()
