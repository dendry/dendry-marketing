import os.path
from fabric.api import *

env.host_string = "ec2-184-72-250-99.compute-1.amazonaws.com"
env.user = "ubuntu"

HERE = os.path.abspath(os.path.dirname(__file__))

class SiteManager(object):
    def __init__(self, proj, diry=None):
        self.proj = proj
        self.diry = diry if diry else os.path.join(HERE, self.proj)

    def send_conf(self):
        put("%s/conf/nginx.conf" % HERE, "/var/www/%s/" % self.proj)
        sudo("service nginx reload")

    def one_time_server_setup(self):
        sudo("mkdir /var/www/%s/" % self.proj)
        sudo("chown ubuntu:ubuntu /var/www/%s/" % self.proj)
        run("mkdir /var/www/%s/content/" % self.proj)

    def one_time_nginx_setup(self):
        self.send_conf()
        sudo("ln -s /var/www/%s/nginx.conf /etc/nginx/sites-available/%s" % (
                self.proj, self.proj))
        sudo("ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s"
             % (self.proj, self.proj))
        sudo("service nginx reload")

    def one_time_setup(self):
        self.one_time_server_setup()
        self.one_time_nginx_setup()

    def prepare(self):
        pass

    def package(self):
        pass

    def send(self):
        pass

    def deploy(self):
        self.prepare()
        self.package()
        self.send()

class StaticSiteManager(SiteManager):
    """
    For handling static site generators with a build script.
    """
    def prepare(self):
        with lcd(self.diry):
            local("jekyll build")

    def package(self):
        with lcd(self.diry):
            local("tar -cf /tmp/%s.tar _site" % self.proj)
        local("gzip -f /tmp/%s.tar" % self.proj)

    def send(self):
        put("/tmp/%s.tar.gz" % self.proj, "/tmp/")
        with cd("/var/www/%s/content/" % self.proj):
            run("rm -rf *")
            run("tar xfz /tmp/%s.tar.gz --strip-components=1" % self.proj)
        self.send_conf()

# ---------------------------------------------------------------------------

main = StaticSiteManager("dendry.org")

def prepare(): main.prepare()
def package(): main.package()
def send(): main.send()
def deploy(): main.deploy()
def send_conf(): main.send_conf()
def one_time_server_setup(): main.one_time_server_setup()
def one_time_nginx_setup(): main.one_time_nginx_setup()
def one_time_setup(): main.one_time_setup()
