import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

import models
import decorators
from posts import app
from database import session

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