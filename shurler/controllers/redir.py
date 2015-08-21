import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from shurler.lib.base import BaseController, render

log = logging.getLogger(__name__)

# import some useful modules 
from os import getcwd
from pylons import app_globals as g
import random
import string
from datetime import datetime
from datetime import timedelta
from sqlalchemy import and_, or_
from shurler.model.meta import Session
from shurler.model import Redir, User, Counter, Visitor
from pylons.decorators import jsonify
from pylons.decorators.secure import authenticate_form
from shurler.lib import qrlib as qrl
from collections import defaultdict



class RedirController(BaseController):
    char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits
    serv_port = 'http://'+request.environ['SERVER_NAME']+':'+request.environ['SERVER_PORT']+'/'
    qr_store =  getcwd() + '/shurler/public/'+g.qr_dir+'/'
    qr_url = serv_port+g.qr_dir+'/'
    
    # riak-related attributes
    rdb = g.rdb
    rbucket = rdb.bucket(g.riak_bucket)

    def set_redir_cookie(self):
        session['shorturls'] = {}
        session.save()
    
    def get_redir_cookie(self):
        return session['shorturls']

    def index(self):
        # Return a rendered template
        #return render('/redir.mako')
        # or, return a string
        sh_cookie = request.cookies.get('shurler')
        if not sh_cookie:
            self.set_redir_cookie()
        else:
            c.short_dict = self.get_redir_cookie()
            #print c.short_dict
       
        # pass the global object to context 
        c.g = g
        return render('/home/home.jinja2')

    def ratelimit(self, now, ipaddr):
        t0 = now - timedelta(minutes=60)

        sub_count = Session.query(Redir).filter(and_((Redir.ipaddr == ipaddr),(Redir.created.between(t0,now)))).count()
        if (sub_count > g.limit_per_hour):
            return False
        return True
    
    @jsonify
    @authenticate_form
    def riak_submit(self):
        out = {}
        if request.method == 'POST':
            shurl = request.POST.get('short').strip()

            riak_qry = self.rdb.add(g.riak_bucket)
            mapf = str("function(v){var data = JSON.parse(v.values[0].data); if(data.long == \""+str(shurl)+"\") { return [[v.key, data]]; } return []; }")
            print mapf
            print riak_qry
            
            riak_qry.map(mapf)
           
            qr_res  = riak_qry.run()
           
            # the url submitted is already in the bucket
            if len(qr_res) > 0:
                print 'esiste: '+(qr_res[0])[0]
                
                genshurl = (qr_res[0])[0]
                reply = self.serv_port+genshurl
                if g.qr_enable :
                    qr_reply = self.qr_url+genshurl+'.png'
                    out = {'short': reply, 'qrcode':qr_reply} 
                else:
                    out = {'short': reply} 
                
                return out

            # ratelimit ctl
            rip = request.environ['REMOTE_ADDR']
            if not g.rl.check(rip):
            #if not self.ratelimit(datetime.now(),rip):
                rate_limit_ok = False
                out = {'RATE_LIMIT': rate_limit_ok}
                return out

            rate_limit_ok = True
            
            # compute a new shorten
            gs_ex = True
    
            while gs_ex: 
                genshurl = ''.join(random.choice(self.char_set) for x in range(6))
                gs_ex_count = self.rbucket.get(str(genshurl)).get_data()
                print 'iloop' 
                if gs_ex_count == None:
                    print 'short url does not exist'
                    gs_ex = False

            new_url = self.rbucket.new(genshurl, data = {
                                        'long' : shurl,
                                        'created_at': datetime.now().isoformat(), 
                                            } )
            new_url.store()
            
            # form the full short url
            short_reply = self.serv_port+genshurl
            session['shorturls'][shurl] = short_reply
            session.save()
            
            if g.qr_enable:
                qr = qrl.QRCode(8, qrl.QRErrorCorrectLevel.H)
                qr.addData(self.serv_port+genshurl)
                qr.make()

                im = qr.makeImage()
                # thumbnail with nearest algorithm
                im.thumbnail(g.qr_pixel_size)
            
                im.save(self.qr_store+genshurl+'.png')
            
                print self.qr_store+genshurl+'.png'

                qr_reply = self.qr_url+genshurl+'.png'
                out = {'short': short_reply, 'qrcode': qr_reply, 'RATE_LIMIT': rate_limit_ok}
                return out
            
            # format and send the reply
            out = {'RATE_LIMIT': rate_limit_ok, 'short': short_reply}
            return out
            #rec = self.rbucket.get('aaaaaa')
            #print rec.get_data()

            #ex_qr = self.rdb.search(g.riak_bucket, 'long:'+shurl).run()

            #for result in ex_qr:
            #    print 'qualcosa'
            
            #print "riak_qr run() length: "+len(ex_qr)
            
    @jsonify
    @authenticate_form     
    def submit(self):
        out = {}
        if request.method == 'POST':
            shurl = request.POST.get('short').strip()

            # check if url is well formed is prformed client side
            # with a javascript check
            lurl_x = Session.query(Redir).filter(Redir.long == shurl)
            lurl_x_count = lurl_x.count()

            # we already have a shorten for the url
            if lurl_x_count == 1:
                entry = lurl_x.one()
                genshurl = entry.short
                
                reply = self.serv_port+genshurl
                out = {'short': reply} 
                return out
            
            # compute a new shorten
            gs_ex = True
    
            while gs_ex: 
                genshurl = ''.join(random.choice(self.char_set) for x in range(6))
                gs_ex_count = Session.query(Redir).filter(Redir.short == genshurl).count()
            
                if gs_ex_count == 0:
                    gs_ex = False

            # ratelimit ctl
            rip = request.environ['REMOTE_ADDR']
            if not g.rl.check(rip):
            #if not self.ratelimit(datetime.now(),rip):
                rate_limit_ok = False
                out = {'RATE_LIMIT': rate_limit_ok}
                return out

            rate_limit_ok = True

            if not g.anon:
                rip = request.environ['REMOTE_ADDR']
            else:
                rip = g.anon_string
            # add the shorten to the database 
            ne = Redir(genshurl,shurl, datetime.now(), rip, cby=None)                
            Session.add(ne)
            # commit to database
            Session.commit()
            
            nc = Counter(ne.id)
            Session.add(nc)
            Session.commit()
            
            # form the full short url
            short_reply = self.serv_port+genshurl
            session['shorturls'][shurl] = short_reply
            session.save()
            
            if g.qr_enable:
                qr = qrl.QRCode(8, qrl.QRErrorCorrectLevel.H)
                qr.addData(self.serv_port+genshurl)
                qr.make()

                im = qr.makeImage()
                # thumbnail with nearest algorithm
                im.thumbnail(g.qr_pixel_size)
            
                im.save(self.qr_store+genshurl+'.png')
            
                print self.qr_store+genshurl+'.png'

                qr_reply = self.qr_url+genshurl+'.png'
                out = {'short': short_reply, 'qrcode': qr_reply, 'RATE_LIMIT': rate_limit_ok}
                return out
            
            # format and send the reply
            out = {'RATE_LIMIT': rate_limit_ok, 'short': short_reply}
            return out
    
    @jsonify
    def get_user_shorturls(self):
        out = {}
        if request.method == 'GET':
            return out;

        if len(session['shorturls']) > 0:
            out = {'urls': [{'short': s, 'long': l}  for l,s in session['shorturls'].items()]}

        return out
     
    def r(self,id):
        if request.method == 'GET':
            lurlq = Session.query(Redir).filter(Redir.short == id)
            
            if lurlq.count() == 1:
                lurl = lurlq.one()
                if g.anon:
                    rip = g.anon_string
                else:
                    rip = request.environ['REMOTE_ADDR']
                
                Session.query(Counter).filter(Counter.short_id == lurl.id).update({Counter.counter: Counter.counter + 1})

                nv = Visitor(lurl.id, rip, datetime.now(), request.environ['HTTP_USER_AGENT'])
                Session.add(nv)
                Session.commit() 

                redirect(lurl.long,code=301)
            else:
                redirect(url('/'), code=301)
