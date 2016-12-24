import cgi
import os
import md5
import datetime
import re
import sys
import urllib
import urlparse
import unicodedata

from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from appengine_utilities import sessions

# Set to true if we want to have our webapp print stack traces, etc
_DEBUG = True
class FreshPage(webapp.RequestHandler):
  @staticmethod
  def get(self):
    pass
    #q= Page.all()
    #q.order("-modified")

    #q = db.GqlQuery("SELECT name FROM Page"+
                    #"ORDER BY modified DESC")
                
    #results = q.fetch(100)
    #for p in results:
    # print "%s<br>" % (p.name)
    query = datastore.Query('Page')
    query.Order(('created',datastore.Query.DESCENDING))
    #query['name ='] = name
    entities = query.Get(100)
    
    strhead = '<table id="freshtable" width="630" border="1px">' + '<tr>'+'<td width="150">Title</td><td width="120">Author</td><td width="180">Create Time</td><td width="180">Last Modify</td>'+'</tr>'

    if len(entities) < 1:
      print 'No article exists!'
      return
    else:
      for p in entities:     
        title = urllib.unquote(p['name'].encode('utf-8'))
        pageid = p['pageid']
        author = p['user'].encode('utf-8')
        createtime = p['created'].strftime("%Y-%m-%d %H:%M:%S").encode('utf-8')
        modifytime = p['modified'].strftime("%Y-%m-%d %H:%M:%S").encode('utf-8')
        strmid = '<tr>'
        strmid +='<td>'+'<a href="/'+str(pageid)+'">'+title+'</a> '+'</td>'
        strmid +='<td>'+author+'</td>'
        strmid +='<td>'+createtime+'</td>'
        strmid +='<td>'+modifytime+'</td>'
        strmid +='</tr>'
        
        strhead +=strmid
    strhead += '</table>'
    
    self.sess = sessions.Session()
    
    if not 'id' in self.sess:    
      values = {
      'msg': strhead,
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''      
        }
    else:
      values = {
      'msg': strhead,
      'lb' : '<!--',
      'le' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',      
      'username' : self.sess['id']       
      }
      
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', 'base.html'))
    self.response.out.write(template.render(path, values, debug=_DEBUG))

    
class SearchPage(webapp.RequestHandler):
  @staticmethod
  def get(self):
    
    page_name = self.request.get('textfield')
   
    #entity = Page.exists(urllib.unquote(page_name))
    tmp = urllib.quote(page_name.encode('utf-8'))
    entity = Page.exists(tmp)
    if entity:
      self.redirect('/'+str(entity['pageid']))
      #print urllib.unquote(tmp)+'<br>'+tmp


      return
    else:
      self.sess = sessions.Session()
    
      if not 'id' in self.sess:    
        values = {
        'msg': '<img src="/static/images/noarticle.jpg" alt="noarticle" name="noarticle" width="200" height="200" id="noarticle" /><br><a href="/">Back to Home Page</a>', 
        'wb' : '<!--',
        'we' : '-->',
        'ebuttonb' :  '<!--',
        'ebuttone' : '-->',
        'username' : ''      
        }
      else:
        values = {
        'msg': '<img src="/static/images/noarticle.jpg" alt="noarticle" name="noarticle" width="200" height="200" id="noarticle" /><br><a href="/">Back to Home Page</a>', 
        'lb' : '<!--',
        'le' : '-->',
        'ebuttonb' :  '<!--',
        'ebuttone' : '-->',      
        'username' : self.sess['id']       
        }
      
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG))


class ExitPage(webapp.RequestHandler):
  @staticmethod 
  def get(self):
    self.sess = sessions.Session()
    self.sess.delete()
    self.redirect('/')
    
    
class MainPage(webapp.RequestHandler):
  def get(self): 
    self.sess = sessions.Session()
    
    if not 'id' in self.sess:    
      values = {
      'msg': '<h1>website constructing....</h1>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''      
      }
    else:
      values = {
      'msg': '<h1>website constructing....</h1>', 
      'lb' : '<!--',
      'le' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',      
      'username' : self.sess['id']       
      }
      
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', 'base.html'))
    self.response.out.write(template.render(path, values, debug=_DEBUG))

class LoginPage(webapp.RequestHandler):
  @staticmethod
  def get(self):
    self.sess = sessions.Session()      
    if not 'id' in self.sess:    
      values = {
      'msg': '', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''      
      }
    else:
      values = {
      'msg': '', 
      'lb' : '<!--',
      'le' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : self.sess['id']       
      }
    
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', 'login.html'))
    self.response.out.write(template.render(path, values, debug=_DEBUG))
  @staticmethod
  def post(self):
    self.sess = sessions.Session()
    id = self.request.get('id').encode('utf8')
    psw = self.request.get('psw').encode('utf8')
    
    
    identification = md5.new()
    identification.update(id)
    identification.update(psw)
    identification.update('kenshin')
     
    iddigest = identification.hexdigest( )  
    
    
    query = datastore.Query('UserData')
    query['iddigest ='] = iddigest
    checkidentities = query.Get(1)
    if checkidentities and checkidentities[0]['iddigest'] == iddigest:
      self.sess['id'] = checkidentities[0]['id']
      self.sess['iddigest'] = checkidentities[0]['iddigest']
      self.redirect('/')
    else:
      values = {
      'msg': '<img src="/static/images/pswerror.jpg" alt="pswerror" name="pswerror" width="200" height="200" id="logo" /><br><a href="/login">Back to Previous Page</a>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''       
      }
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG)) 
        
class RegisterPage(webapp.RequestHandler):
  @staticmethod
  def get(self):
    self.sess = sessions.Session()
    
    if not 'id' in self.sess:    
      values = {
      'msg': '', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''      
      }
    else:
      values = {
      'msg': '', 
      'lb' : '<!--',
      'le' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : self.sess['id']       
      }
    
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', 'register.html'))
    self.response.out.write(template.render(path, values, debug=_DEBUG))
  @staticmethod   
  def post(self):
    id = self.request.get('id')
    psw = self.request.get('psw')
    pswa = self.request.get('pswa')
    sex = self.request.get('sex')
    email = self.request.get('email')
    msn = self.request.get('msn')
    qq = self.request.get('qq')
    
    
    idlength = len(id)
    if idlength < 6:
      values = {
      'msg': '<img src="/static/images/idlengtherror.jpg" alt="error" name="error" width="200" height="200" id="idlengtherror" /><br><a href="/register">Back to Previous Page</a>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''       
      }
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG))
      return    
    
    
    if psw != pswa:
      values = {
      'msg': '<img src="/static/images/mimabutong.jpg" alt="logo" name="error" width="200" height="200" id="logo" /><br><a href="/register">Back to Previous Page</a>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''       
      }
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG))
      return
      
    #check the id wether only one
    query = datastore.Query('UserData')
    query['id ='] = id
    checkidentities = query.Get(1)
    if checkidentities and checkidentities[0]['id'] == id:
      values = {
      'msg': '<img src="/static/images/idrepeate.jpg" alt="idrepeate" name="idrepeate" width="200" height="200" id="logo" /><br><a href="/register">Back to Previous Page</a>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''       
      }
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG))
      return
      
    #check the email wether only one
    query = datastore.Query('UserData')
    query['email ='] = email
    checkidentities = query.Get(1)
    if checkidentities and checkidentities[0]['email'] == email:
      values = {
      'msg': '<img src="/static/images/emailrepeat.jpg" alt="emailrepeat" name="emailrepeat" width="200" height="200" id="emailrepeat" /><br><a href="/register">Back to Previous Page</a>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''       
      }
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG))
      return

    
    #computer md5 digest
    try:
      identification = md5.new()
      identification.update(id)
      identification.update(psw)
      identification.update('kenshin')
    except UnicodeEncodeError:
      values = {
      'msg': '<img src="/static/images/nochinese.jpg" alt="nochinese" name="nochinese" width="200" height="200" id="nochinese" /><br><a href="/register">Back to Previous Page</a>', 
      'wb' : '<!--',
      'we' : '-->',
      'ebuttonb' :  '<!--',
      'ebuttone' : '-->',
      'username' : ''       
      }
      directory = os.path.dirname(__file__)
      path = os.path.join(directory, os.path.join('templates', 'base.html'))
      self.response.out.write(template.render(path, values, debug=_DEBUG))
      return
    
    iddigest = identification.hexdigest( )      
    now = datetime.datetime.utcnow() + datetime.timedelta( hours=+8 )
    
    entity = datastore.Entity('UserData')
    entity['id'] = id
    entity['created'] = now
    entity['iddigest'] = iddigest
    entity['sex'] = sex
    entity['email'] = email
    entity['msn'] = msn
    entity['qq'] = qq
    
    datastore.Put(entity)
    
    #register success add session
    self.sess = sessions.Session()
    self.sess['id'] = id
    self.sess['iddigest'] = iddigest
    
    values = {
    'msg': '<img src="/static/images/success.jpg" alt="success" name="success" width="200" height="200" id="logo" /><br><a href="/">Congratulations!</a>', 
    'wb' : '<!--',
    'we' : '-->',
    'ebuttonb' :  '<!--',
    'ebuttone' : '-->',
    'username' : ''       
    }
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', 'base.html'))
    self.response.out.write(template.render(path, values, debug=_DEBUG))
    



class BaseRequestHandler(webapp.RequestHandler):

  def generate(self, template_name, template_values={}):
    self.sess = sessions.Session()
    
    if not 'id' in self.sess:    
      values = {
      'msg': '<h1>welcome</h1>', 
      'wb' : '<!--',
      'we' : '-->',
      'username' : ''  ,
      'application_name': 'BulletWiki'    
      }
    else:
      values = {
      'msg': '<h1>website constructing....</h1>', 
      'lb' : '<!--',
      'le' : '-->',
      'username' : self.sess['id'] ,
      'application_name': 'BulletWiki'   
      }
      

    values.update(template_values)
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', template_name))
    self.response.out.write(template.render(path, values, debug=_DEBUG))
  
  def head(self, *args):
    pass
  
  def get(self, *args):
    pass
    
  def post(self, *args):
    pass


class WikiPage(BaseRequestHandler):

  def get(self, page_name):

    
    if page_name and page_name == 'login':
      LoginPage.get(self)
      return
    elif page_name and page_name == 'register':
      RegisterPage.get(self)
      return
    elif page_name and page_name == 'exit':
      ExitPage.get(self)
      return
    elif page_name and page_name == 'search':
      SearchPage.get(self)
      return
    elif page_name and page_name == 'fresh':
      FreshPage.get(self)
      return
      
      
    
      
      

    if not page_name:
      page_name = 'MainPage'
    page = Page.loadbyid(page_name)

    
    
 
      


    if not page.entity:
      mode = 'edit'
    else:
      modes = ['view', 'edit']
      mode = self.request.get('mode')
      if not mode in modes:
        mode = 'view'


    self.sess = sessions.Session()
    if mode == 'edit' and not 'id' in self.sess:
      self.redirect('/login')
      return

    if mode == 'edit':
      entity = Page.existsbyid(page_name)
      if page_name and entity:
        if self.sess['id'] != entity['user']:

          values = {
          'msg': '<img src="/static/images/cantedit.jpg" alt="cantedit" name="cantedit" width="200" height="200" id="logo" /><br><a href="/">Can not Edit Others Wiki Page</a>', 
          'lb' : '<!--',
          'le' : '-->',
         'username' : self.sess['id']       
          }
          directory = os.path.dirname(__file__)
          path = os.path.join(directory, os.path.join('templates', 'base.html'))
          self.response.out.write(template.render(path, values, debug=_DEBUG))
          return
    
    
    
    


    self.generate(mode + '.html', {
      'page': page,
    })

  def post(self, page_name):
    """???post???????????wiki????????????.??????????post???? 
    
    Args:
      page_name: ??wiki???.
    """
    
    if page_name and page_name == 'login':
      LoginPage.post(self)
      return
    elif page_name and page_name == 'register':
      RegisterPage.post(self)
      return  
        
      

    self.sess = sessions.Session()
    if not 'id' in self.sess:
      self.redirect('/login')
      return

    if not page_name:
      self.redirect('/')
      return
      

    entity = Page.existsbyid(page_name)
    if page_name and entity:
      if self.sess['id'] != entity['user']:

        values = {
        'msg': '<img src="/static/images/cantedit.jpg" alt="cantedit" name="cantedit" width="200" height="200" id="logo" /><br><a href="/">Can not Edit Others Wiki Page</a>', 
        'lb' : '<!--',
        'le' : '-->',
        'username' : self.sess['id']       
        }
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', 'base.html'))
        self.response.out.write(template.render(path, values, debug=_DEBUG))
        return

        



  
    page = Page.loadbyid(page_name)

    page.content = self.request.get('content')
        
    page.save()
    
        
    self.redirect(page.view_url())
    


class Page(object):

  def __init__(self, name, entity=None):
    self.name = name
    self.entity = entity
    if entity:
      self.content = entity['content']
      self.pageid = entity['pageid']
      if entity.has_key('user'):
        self.user = entity['user']
      else:
        self.user = None
      self.created = entity['created']
      self.modified = entity['modified']
    else:

      now = datetime.datetime.utcnow() + datetime.timedelta( hours=+8 )
      #self.content = '<h1>%s</h1>' % (cgi.escape(name),)
      
      self.content = '<h1>'+urllib.unquote(name)+'</h1>'
      self.user = None
      self.created = now
      self.modified = now

  def entity(self):
    return self.entity

  def edit_url(self):
    return '/%s?mode=edit' % (self.name,)

  def view_url(self):
    query = datastore.Query('Page')
    query['name ='] = self.name
    entities = query.Get(1)
    if len(entities) < 1:
      return '/'+self.name
    else:
      return '/'+str(entities[0]['pageid'])   

  def wikified_content(self):

    
    #transforms = [
    #  AutoLink(),
    #  WikiWords(),
    #  HideReferers(),
    #]
    transforms = [
       AutoLink()
    ]
       
    
    content = self.content
    for transform in transforms:
      content = transform.run(content)
    return content
    

  def save(self):

    now = datetime.datetime.utcnow() + datetime.timedelta( hours=+8 )
    
    

    if self.entity:
      entity = self.entity
    else:
    
      querycounter = datastore.Query('Counter')
      counterentities = querycounter.Get(1)
      if len(counterentities) < 1:
        counterentity = datastore.Entity('Counter')
        counterentity['num'] = 1
        num = 1
        datastore.Put(counterentity)
      else:
        num = counterentities[0]['num']+1    
        counterentities[0]['num'] = num
        datastore.Put(counterentities[0])

      
      entity = datastore.Entity('Page')
      entity['name'] = self.name
      entity['created'] = now         
      entity['pageid'] = num
      
      
    entity['content'] = datastore_types.Text(self.content)
    entity['modified'] = now


    self.sess = sessions.Session()
    if 'id' in self.sess:
      entity['user'] = self.sess['id']
    else:
      return
    

    datastore.Put(entity)

  @staticmethod
  def load(name):

    query = datastore.Query('Page')
    query['name ='] = name
    entities = query.Get(1)
    if len(entities) < 1:
      return Page(name)
    else:
      return Page(name, entities[0])
      
  @staticmethod
  def loadbyid(name):

    
    try:
      query = datastore.Query('Page')   
      query['pageid ='] = int(name)
      entities = query.Get(1)
      if len(entities) < 1:
        return Page(name)
      else:
        return Page(name, entities[0])
    except ValueError:

      query = datastore.Query('Page')   
      query['name ='] = name
      entities = query.Get(1)
      if len(entities) < 1:
        return Page(name)
      else:
        return Page(name, entities[0])
      
        
    

  @staticmethod
  def exists(name):

    return Page.load(name).entity

  @staticmethod
  def existsbyid(name):

    return Page.loadbyid(name).entity


class Transform(object):

  def run(self, content):

    parts = []
    offset = 0
    for match in self.regexp.finditer(content):
      parts.append(content[offset:match.start(0)])
      #print content[offset:match.start(0)]
      parts.append(self.replace(match))
      #print self.replace(match)
      offset = match.end(0)
    parts.append(content[offset:])
    return ''.join(parts)




class WikiWords(Transform):

  def __init__(self):
    self.regexp = re.compile(r'[A-Z][a-z]+([A-Z][a-z]+)+')
    #self.regexp = re.compile(ur'\w+')

  def replace(self, match):
    wikiword = match.group(0)
    if Page.exists(wikiword):
      return '<a class="wikiword" href="/%s">%s</a>' % (wikiword, wikiword)  
    else:
      return wikiword



class AutoLink(Transform):

  def __init__(self):
    self.regexp = re.compile(r'([^"])\b((http|https)://[^ \t\n\r<>\(\)&"]+' \
                             r'[^ \t\n\r<>\(\)&"\.])')

  def replace(self, match):
    url = match.group(2)
    return match.group(1) + '<a class="autourl" href="%s">%s</a>' % (url, url)


class HideReferers(Transform):

  def __init__(self):
    self.regexp = re.compile(r'href="(http[^"]+)"')

  def replace(self, match):
    url = match.group(1)
    scheme, host, path, parameters, query, fragment = urlparse.urlparse(url)
    #url = 'http://www.google.com/url?sa=D&amp;q=' + urllib.quote(url)
    url = '' + url
    return 'href="%s"' % (url,)

   
        
              

application = webapp.WSGIApplication([('/(.*)', WikiPage)],debug=_DEBUG)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()