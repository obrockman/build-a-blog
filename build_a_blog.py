import os 
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                    autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True) 
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("front.html", title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog ) #dont need created, added automatically 
            b.put()

            self.redirect("/blog") #redirects do a get 
        else: 
            error = "We need both a title and a blog post!"
            self.render_front(title, blog, error)

class BlogPage(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("all_blogs.html", blogs=blogs)

class ViewPostHandler(Handler):
    def get(self, id):       
        id = int(id)
        blog = Blog.get_by_id(id) 
        if blog:
            self.render("one_blog.html", blog=blog) #first var name matching in tempalte, second = var here 
        else: 
            error = "Sorry this is not a post."
            self.render("error.html", error=error)

        

app = webapp2.WSGIApplication([('/', MainPage),
                                ('/blog',BlogPage),
                                webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], 
                                debug = True)