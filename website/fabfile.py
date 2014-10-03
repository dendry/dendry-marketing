import sys
import os.path
from fabric.api import *

env.host_string = "ec2-184-72-250-99.compute-1.amazonaws.com"
env.user = "ubuntu"

HERE = os.path.abspath(os.path.dirname(__file__))

class SiteManager(object):
    def __init__(self, proj, diry=None):
        self.proj = proj
        self.diry = diry if diry else os.path.join(HERE, self.proj)

    def _export(self, prefix=''):
        """
        Sets the methods of this instance to be the global fab commands.
        """
        module = sys.modules[__name__]
        class_ = self.__class__

        # Build a list of method names to export.
        method_names = set()
        def _add_methods(class_):
            for name in class_.__dict__:
                if not name.startswith('_') and callable(getattr(class_, name)):
                    method_names.add(name)
        _add_methods(class_)
        for parent in class_.__mro__:
            _add_methods(parent)

        # Create methods to call the correct function
        def make_proxy(method_name, module_name):
            def proxy(): getattr(self, method_name)()
            proxy.func_name = module_name
            return proxy
        for name in method_names:
            module_name = prefix + name
            setattr(module, module_name, make_proxy(name, module_name))

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


class JekyllStaticSiteManager(SiteManager):
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

JekyllStaticSiteManager("dendry.org")._export()
