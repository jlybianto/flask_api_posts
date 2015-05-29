import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

import models
import decorators
from posts import app
from database import session

# JSON Schema describing the structure of a post
post_schema = {
    "properties": {
        "title" : {"type" : "string"},
        "body" : {"type": "string"}
    },
    "required" : ["title", "body"]
}

@app.route("/api/posts", methods=["GET"])
@decorators.accept("application/json")
def posts_get():
    """ Get a list of posts """
    # Get the query string arguments for title
    title_like = request.args.get("title_like")
    
    # Get the query string arguments for body
    body_like = request.args.get("body_like")
    
    # Get the posts from the database
    posts = session.query(models.Post)
    
    # Add filter from 'title_like' and 'body_like' query string
    if title_like and body_like:
        posts = posts.filter(models.Post.title.contains(title_like)).\
                    filter(models.Post.body.contains(body_like))
    
    # Add filter from 'title_like' query string
    if title_like:
        posts = posts.filter(models.Post.title.contains(title_like))
    
    # Add filter from 'body_like' quert string
    if body_like:
        posts = posts.filter(models.Post.body.contains(body_like))
    
    posts = posts.all()
    
    # Convert the posts to JSON and return a response
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/posts/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def post_get(id):
    """ Single post endpoint """
    
    # Get the post from the database
    post = session.query(models.Post).get(id)
    
    # Check whether the post exists
    # If no, return a 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    # If yes, return the post as JSON
    data = json.dumps(post.as_dictionary())
    return Response(data, 200, mimetype="application/json")

@app.route("/api/posts/<int:id>", methods=["DELETE"])
@decorators.accept("application/json")
def post_delete(id):
    """ Delete single post endpoint """
    
    # Get the post from the database
    post = session.query(models.Post).get(id)
    
    # Check whether the post exists
    # If no, return a 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    # If yes, delete the post from database with confirmation message
    session.delete(post)
    session.commit()
    message = "Deleted post with id {} from database".format(id)
    data = json.dumps({"message": message})
    return Response(data, 200, mimetype="application/json")

@app.route("/api/posts", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def posts_post():
    """ Add a new post """
    # To access the data passed into the endpoint
    data = request.json
    
    # Check that the JSON supplied is valid
    # If not, return a 422 Unprocessable Entity
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")    
    
    # Add the post to the database
    post = models.Post(title=data["title"], body=data["body"])
    session.add(post)
    session.commit()
    
    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(post.as_dictionary())
    headers = {"Location": url_for("post_get", id=post.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")

@app.route("/api/posts/<int:id>", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def posts_edit(id):
    """ Edit a post """
    # To access the data passed into the endpoint
    data = request.json
    
    # Get the post from the database
    post = session.query(models.Post).get(id)
    
    # Check whether the post exists
    # If no, return a 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # If yes, gives ability to edit the post
    post.title = data["title"]
    post.body = data["body"]
    session.add(post)
    session.commit()
    return Response(data, 200, mimetype="application/json")